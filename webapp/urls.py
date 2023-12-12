from django.urls import path

from . import views

urlpatterns = [
    path("professor/", views.professor, name="professor"),
    path("professor/createproject/", views.create_project, name="create_project"),
    path("professor/project/<project_dir>/", views.solutions, name="project_solutions"),
    path("professor/edit/<project_dir>/", views.edit, name="edit_project"),
    path("professor/project/<project_dir>/<user_name>/", views.correction,name="correction"),
    path("student/", views.student, name="student"),
    path("login/", views.logining, name="login"),
]