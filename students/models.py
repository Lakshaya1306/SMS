from django.db import models
from django.contrib.auth.models import User

class courses(models.Model):
    name = models.CharField(max_length=100, null=False)
    department = models.CharField(max_length=100)
    HOD = models.CharField(max_length=100)
    year  = models.IntegerField(default = 1)
    semester = models.IntegerField(default = 1)
    enrolled_students = models.IntegerField()
    

class students(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    fatherName = models.CharField(max_length=20, null=True)
    motherName = models.CharField(max_length=20, null=True)
    contact = models.BigIntegerField(blank=False, null=False)
    dob = models.CharField(null=False, max_length=10)
    branch = models.CharField(max_length=50, null=False)
    yos = models.IntegerField(null=False)
    semester = models.IntegerField(default=1)
    address = models.CharField(null=False, max_length=200)
    course = models.ManyToManyField(courses, through='enrollment')
    
class enrollment(models.Model):
    enrolledStatus = [
        ('ongoing', 'ongoing'),
        ('pass', 'pass'),
        ('fail', 'fail'),
    ]
    student = models.ForeignKey(students, on_delete=models.CASCADE)
    course = models.ForeignKey(courses, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=7,choices = enrolledStatus)