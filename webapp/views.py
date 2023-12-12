import os
import pandas as pd
import datetime
import webapp.umlapi as uml


from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.files.storage import FileSystemStorage
from .models import Project, Student, Solution
from UMLCorrect.settings import MEDIA_ROOT
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from webapp.correction import check_all,anticheat


# Create your views here.

# Global Variables

student_group = "Student"
groups = {"TODO"}
urls = {"login": "/login/", "student": "/student/","professor": "/professor/", "professor_edit" : "/professor/edit/", "professor_create": "/professor/create"}
htmls = {"student": "student.html", "login": "login.html", "correct": "correct.html"}

# Additional (maybe externalize to API)

def next_temp():
    temp_list = os.listdir(MEDIA_ROOT)
    temp_list.sort()
    i = 1
    name = "temp"
    for dir in temp_list:
        if name in dir:
            if not int(dir[4:]) == i:
                return name + str(i)
            i += 1
    return name + str(i)


def save_to_dir(dir, file):
    fs = FileSystemStorage()
    filename = fs.save(dir, file)
    return fs.path(filename)

def delete_from_dir(dir):
    try:
        os.remove(dir)
    except OSError as e:
        print("Error %s while deleting %s" % (e.strerror, e.filename))

def delete_dir(dir):
    project_dir = media_path(dir)
    print(os.listdir(project_dir))
    for file in os.listdir(project_dir):
        print(file)
        delete_from_dir(os.path.join(project_dir, file))
    if not len(os.listdir(project_dir)) == 0:
        print("There was an error while deleting the project files, aborting project deletion")
        return False
    else:
        os.rmdir(project_dir)
        print("Successfully deleted")
        return True

def create_student(name, lastname, id, email):
    Group.objects.get_or_create(name=student_group)
    username = ""
    username += str(name)[0]
    lastname_split = str(lastname).split()
    username_ok = False
    i = 2
    username += lastname_split[0] + lastname_split[-1][0]
    temp_username = username

    while not username_ok:
        if User.objects.filter(username=temp_username).exists():
            temp_username = username + str(i)
            i += 1
        else:
            username_ok = True
    username = temp_username
    user = User.objects.create_user(username, email=email, password=id)
    user.first_name = name
    user.last_name = lastname
    user.save()
    student = Student(user=user)
    student.save()
    user.groups.add(Group.objects.get(name=student_group))

    return student

def change_dir_name(dir):
    temp_list = os.listdir(MEDIA_ROOT)
    temp_list.sort()
    i = 1
    not_found = True
    while not_found:
        if str(i) in temp_list:
            i += 1
        else:
            not_found = False
    new_dir = media_path(str(i))
    old_dir = media_path(dir)
    os.mkdir(new_dir)
    for file in os.listdir(old_dir):
        os.replace(os.path.join(old_dir, file), os.path.join(new_dir, file))
    delete_dir(old_dir)
    return i

def delete_project(project):
    if not project.dir in os.listdir(MEDIA_ROOT) or delete_dir(project.dir):
        project_students = Student.objects.filter(project=project)
        for student in project_students:
            student.user.delete()
            student.delete()
        project.delete()

def remove_dupes(lst):
    if lst:
        aux_list = []
        for elem in lst:
            if elem not in aux_list:
                aux_list.append(elem)
        return aux_list

def redirects(request):
    if not request.user.is_authenticated and not request.path == urls["login"]:
        return HttpResponseRedirect(urls["login"])
    if request.user.groups.filter(name=student_group).exists() and not request.path == urls["student"]:
        return HttpResponseRedirect(urls["student"])
    return False

def time_left(deadline):
    time_left = (deadline - datetime.datetime.now())
    sec_left = time_left.seconds
    days = time_left.days
    hours = sec_left // 3600 # 60 * 60
    mins = sec_left % 3600 // 60
    secs = sec_left % 3600 % 60
    return [days, hours, mins, secs]

def uml_undupped(project_dir):
    aux_project = uml.prepare_uml(project_dir)
    return remove_dupes(aux_project)

def media_path(project_dir):
    return os.path.join(MEDIA_ROOT,str(project_dir))

# Views
def professor(request):
    auth_check = redirects(request)
    if auth_check:
        return auth_check
    if request.method == 'POST':
        primary_key = request.POST["primary_key"]
        deleting_project = Project.objects.get(pk=primary_key)
        delete_project(deleting_project)
        return HttpResponseRedirect(urls["professor"])
    template = loader.get_template("professor.html")
    project_list = Project.objects.order_by("publication_date")
    context = {"project_list": project_list}
    return HttpResponse(template.render(context, request))

def solutions(request, project_dir):
    auth_check = redirects(request)
    if auth_check:
        return auth_check
    template = loader.get_template("solutions.html")
    project = Project.objects.get(dir=project_dir)
    students = project.student_set.all()
    context = {"project": project, "students": students}
    return HttpResponse(template.render(context, request))

def correction(request,project_dir,user_name):
    auth_check = redirects(request)
    if auth_check:
        return auth_check

    if request.method == "POST":
        if request.POST["grade"]:
            student = Student.objects.get(user=User.objects.get(username=user_name))
            student.grade = request.POST["grade"]
            student.save()

    project = Project.objects.get(dir=project_dir)
    student = Student.objects.get(user__username=user_name)
    context = {"project": project, "projectID": project_dir, "student": student.user.first_name + " " + student.user.last_name, "missing": False}
    if student.grade:
        context["grade"] = student.grade
    if not Solution.objects.filter(solution_owner=student).exists():
        context["missing"] = True

    else:
        solution = Solution.objects.get(solution_owner=student)
        class_list = uml_undupped(solution.solution_file.path)
        context["classList"] = class_list
        time_stu = datetime.datetime.now()
        solution_file = uml.prepare_uml(solution.solution_file.path)
        time_stu = datetime.datetime.now()-time_stu
        print("Time to extract from stu:"+str(time_stu.microseconds/1000))
        time_prof = datetime.datetime.now()
        reference = uml.prepare_uml(project.reference.path)
        time_prof = datetime.datetime.now() - time_prof
        print("Time to extract from prof:"+str(time_prof.microseconds/1000))
        given_list = uml.load_project(project.given_list.path)
        time_correc = datetime.datetime.now()
        correction_list = check_all(solution_file,reference,given_list)
        time_correc = datetime.datetime.now()-time_correc
        print("Time to generate correc:"+str(time_correc.microseconds/1000))
        solutions_in_project = Solution.objects.filter(solution_owner__in=Student.objects.filter(project=project)).exclude(solution_owner=student)
        if solutions_in_project:
            if not len(solutions_in_project) > 1:
                solutions_in_project = [solutions_in_project]
            print(solutions_in_project)
            for solution_review in solutions_in_project:
                print(solution_review)
                solution_aux = uml.prepare_uml(solution_review.solution_file.path)
                time_cheat = datetime.datetime.now()
                cheat_index = anticheat(solution_file,solution_aux)
                time_cheat = datetime.datetime.now() - time_cheat
                print("Time to generate cheat index:"+str(time_cheat.microseconds/1000))
                if cheat_index > 0.5:
                    copied_from = solution_review.solution_owner.user.first_name + " " + solution_review.solution_owner.user.last_name
                    correction_list.append("Similarity of "+str(int(cheat_index * 100))+"% found with the solution from "+copied_from)
        context["correction_list"] = correction_list

    if project.deadline < datetime.datetime.now():
        context["correctable"] = True
    template = loader.get_template(htmls["correct"])
    return HttpResponse(template.render(context, request))

def edit(request, project_dir):
    time_publi=datetime.datetime.now()
    auth_check = redirects(request)
    if auth_check:
        return auth_check
    if request.method == "POST":
        project = Project.objects.get(dir=project_dir)
        project.group_name = request.POST["groupName"]
        project.project_name = request.POST["projectName"]
        project_list = uml_undupped(project.reference.path)

        if request.POST["deadline"]:
            project.deadline = request.POST.get("deadline")

        if "studentList" in request.FILES.keys():
            if project.students_file:
                delete_from_dir(project.students_file.path)
            student_file = request.FILES["studentList"]
            students = pd.read_excel(student_file, header=None)
            project.solutions_total = len(students.index)
            students_path = os.path.join(project_dir, "alumnos.xlsx")
            project.students_file = save_to_dir(students_path, student_file)

        if "reference" in request.FILES.keys():
            reference_path = os.path.join(project_dir, "reference.mdj")
            delete_from_dir(media_path(reference_path))
            project.reference = save_to_dir(reference_path, request.FILES["reference"])

        project.save()

        if request.POST.get("publish"):  # Publishing project

            excel_positions = ["name", "lastname", "id", "email"]  # excel formatting

            project.publication_date = datetime.date.today()
            with open(project.students_file.path, encoding="latin-1") as excel_file:
                student_list = pd.read_excel(excel_file.name, header=None).iloc()
                for student in student_list:
                    project_student = create_student(student[excel_positions.index("name")],
                                                     student[excel_positions.index("lastname")],
                                                     student[excel_positions.index("id")],
                                                     student[excel_positions.index("email")])
                    project_student.project = project
                    project_student.save()


            project.dir = change_dir_name(project_dir)
            delete_from_dir(os.path.join(media_path(project.dir),"alumnos.xlsx"))
            given_items = []
            given_elements = []
            for item in request.POST:
                if "class:" in item:
                    given_items.append(item)
                if "relation:" in item:
                    given_items.append(item)
            for item in given_items:
                given_elements.append(uml.get_element_by_id(project_list, item[-20:]))
            project.given_list = uml.save_project(media_path(project.dir),"given_list.txt",given_elements)
            project.reference = media_path(os.path.join(str(project.dir), "reference.mdj"))
            project.save()
            time_publi = datetime.datetime.now()-time_publi
            print("Time to publish:"+str(time_publi.microseconds/1000))
            return HttpResponseRedirect(urls["professor"])

        return HttpResponseRedirect(urls["professor_edit"]+ project_dir)

    template = loader.get_template("modifyproject.html")
    project = Project.objects.get(dir=project_dir)
    if project.deadline:
        deadline = str(project.deadline.date())
    else:
        deadline = ""
    # LOAD UML FUNCTIONALITY
    class_list = uml_undupped(project.reference.path)
    context = {"project": project, "deadline": deadline, "classList": class_list}
    return HttpResponse(template.render(context, request))

def create_project(request):
    auth_check = redirects(request)
    if auth_check:
        return auth_check
    if request.method == "POST":
        uploaded_file = request.FILES.get("file_input")
        if uploaded_file:
            temp_dir = next_temp()
            temp_name = "New Project " + temp_dir[4:]
            file_path = save_to_dir(os.path.join(temp_dir, "reference.mdj"), uploaded_file)
            new_project = Project(reference=file_path, dir=temp_dir, project_name=temp_name)
            new_project.save()
            return HttpResponseRedirect(urls["professor_edit"] + temp_dir)
        else:
            return HttpResponseRedirect(urls["professor_create"])

    return render(request, "uploadproject.html")

def student(request):
    auth_check = redirects(request)
    if auth_check:
        return auth_check

    user = request.user
    student = Student.objects.get(user=user)
    project = student.project

    uploaded_file = request.FILES.get("file_input")
    if uploaded_file:
        reupload = Solution.objects.filter(solution_owner=student).exists()
        if not reupload:
            solution = Solution(solution_owner=student)
            project.solutions_sent += 1
        else:
            delete_from_dir(os.path.join(project.dir,user.username))
            solution = Solution.objects.get(solution_owner=student)
        file_path = save_to_dir(os.path.join(project.dir, user.username + ".mdj"), uploaded_file)
        solution.solution_file = file_path
        solution.solution_date = datetime.datetime.now()
        solution.save()
        project.save()
        return HttpResponseRedirect(urls["student"])

    context = {"project": project.project_name, "group": project.group_name, "deadline": project.deadline}
    template = loader.get_template(htmls["student"])
    if student.grade != None:
        context["grade"] = student.grade
        return HttpResponse(template.render(context, request))

    remaining_time = time_left(project.deadline)
    if remaining_time[0] < 0:
        context["late"] = True
    context["time_left"] = remaining_time
    if Solution.objects.filter(solution_owner=student).exists():
        solution = Solution.objects.get(solution_owner=student)
        context["solution_date"] = solution.solution_date.date()

    return HttpResponse(template.render(context, request))

def logining(request):
    auth_check = redirects(request)
    if auth_check:
        return auth_check
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        context = {}
        template = loader.get_template(htmls["login"])
        if user is not None:
            logout(request)
            login(request,user)
        else:
            context = {"error_message": True}
        if request.user.groups.filter(name=student_group).exists():
            return student(request)
        return HttpResponse(template.render(context, request))
    return (render(request, "login.html"))