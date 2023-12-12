from django.db import models
from django.contrib.auth.models import User
from .validators import validate_mdj, validate_excel

# Create your models here.

"""Model for a project (multiple solutions) """
class Project(models.Model):
    publication_date = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    group_name = models.CharField(max_length=100,default="Not defined")
    project_name = models.CharField(max_length=100)
    solutions_total = models.SmallIntegerField(default=0)
    solutions_sent = models.SmallIntegerField(default=0)
    reference = models.FileField(upload_to="files/",validators=[validate_mdj])
    dir = models.CharField(unique=True,max_length=7)
    students_file = models.FileField(upload_to="files/",validators=[validate_excel], null=True, blank=True)
    reference_list = models.FileField(upload_to="files/",null=True,blank=True)
    given_list = models.FileField(upload_to="files/",null=True,blank=True)

"""Model for the student (user)"""
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING,null=True, blank=True)
    grade = models.DecimalField(max_digits=4,decimal_places=2,null=True, blank=True)

"""Model for a presented solution for a project"""
class Solution(models.Model):
    solution_date = models.DateTimeField()
    solution_file = models.FileField(upload_to="files/",validators=[validate_mdj])
    solution_owner = models.OneToOneField(Student, on_delete=models.CASCADE)



