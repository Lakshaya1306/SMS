from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator

from students.models import students, courses, enrollment 

from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime

# ------------------------------View function related to Registeration and Login functionality-----------------------------------------------------------------------------------------------------------

def registration(request):
    """ Registers the new user into the database after taking details like full name, email and password, and saving the password after hashing it into the database

    Args:
        request (HttpRequest): incoming HTTP Request from the client 

    Returns:
        HttpResponse: Rendered HTML response for the student registration page and after filling the values redirects it to login url
    """
    if request.method == 'POST':    
        userData = request.POST
        fullName = userData.get('full_name')
        email = userData.get('email')
        password = userData.get('password')
    
        firstName, lastName = map(str, fullName.split(" "))
        user = User.objects.create(first_name = firstName, last_name = lastName, email = email, username = email)
        user.set_password(password)
        user.save()
        return redirect('student login')
    
    return render(request, "register.html")

def login(request):
    """Logs in the user after authenticating against username and password field and then binding the user with the session using login() function of django

    Args:
        request (HttpRequest): incoming HTTP request from the client 

    Returns:
        HttpResponse: Rendered HTML response for the student login page and after authenticating the values if user is not superuser it redirects user to url to complete their profile otherwise redirects to the home url
    """
    if request.method == 'POST':
        userData = request.POST
        email = userData.get('email')
        password = userData.get('password')
        try: 
            user = authenticate(username = email, password = password)
            if user:
                auth_login(request, user) 
                studentInstance = students.objects.filter(student_id = user.id).first()
                if user.is_superuser or studentInstance:
                    return redirect('home')
                else:
                    return redirect('complete profile')
            else:
                messages.error(request, "Invalid credentials provided")
                return redirect('student login')
        except Exception as e:
            print(e)
    return render(request, "login.html")

def logout(request):
    """Logs out the user from the session using logout() function of django

    Args:
        request (HttpRequest): incoming HTTP request from the client 

    Returns:
        HttpResponse: redirects the user to login page 
    """
    auth_logout(request)
    return redirect('student login')

def completeProfilePage(request):
    """This function helps the student to complete their profile by filling in the necessary fields and then saving that instance to student and enrollment model

    Args:
        request (HttpRequest): incoming HTTP request from the client

    Returns:
         HttpResponse: renders the HTML response and if user is already registered then redirects the user to home page
    """
    user = request.user
    context = {
        'firstName':user.first_name,
        'lastName':user.last_name, 
        'email':user.email,
    }
    
    if request.method == 'POST':
        studentData = request.POST
        students.objects.create(
            fatherName = studentData.get('fatherName'), 
            motherName = studentData.get('motherName'),
            contact = studentData.get('contact'),
            dob = studentData.get('dob'),
            branch = studentData.get('branch'),
            yos = studentData.get('year'),
            address = studentData.get('address'),
            semester = studentData.get('semester'), 
            student_id = user.id
            )
        
        student = students.objects.get(student_id = user.id)
        
        branch = student.branch
        yos = student.yos
        semester = student.semester
        
        courseqs = courses.objects.filter(department = branch, year = yos, semester = semester)
        
        for course in courseqs:
            enrollment.objects.create(
                course_id = course.id,
                student_id = student.id,
                status = 'Ongoing'
            )
            course.enrolled_students  += 1
            course.save()
        
        return redirect('home')
    
    return render(request, "completeProfilePage.html", context)

def forgotPassword(request):
    """Generates a unique url with the help of user id and one time use token and redirects the user to that new url inorder to recover the password 

    Args:
        request (HttpRequest): incoming HTTP request from the client

    Returns:
         HttpResponse: renders the HTML response and if user is already registered then redirects the user to home page
    """
    if request.method == "POST":
        email = request.POST.get('email')
        user = User.objects.filter(email = email).first()
        
        if user:
            encodedId = urlsafe_b64encode(str(user.id).encode()).decode()
            token = PasswordResetTokenGenerator().make_token(user)
            
            path = reverse('reset password', kwargs={'uid':encodedId, 'token':token})
            url = request.build_absolute_uri(path)
            
            return redirect(url)
        else:
            messages.error(request, "Invalid email")
            return redirect("forgot password")
        
    return render(request, "forgotPassword.html")

def resetPassword(request, uid, token):
    """Provides the functionality for the user to enter a new password and saves it in the db, after authenticating the user against the token and the user id 

    Args:
        request (HttpRequest): incoming HTTP request from the client 
        uid (base64_encoded): encoded user id 
        token (str): one time use tokens 

    Returns:
        HttpResponse: renders the HTML response, if password doesn't matched then renders the same pafe with error message
        and if password matches and is valid then redirects the user to login page otherwise to the forgot password page 
    """
    if request.method == "POST":
        password = request.POST.get("password")
        confirmPassword = request.POST.get("confirmPassword")
        
        if password == confirmPassword:
            userId = int(urlsafe_b64decode(uid).decode())
            user = User.objects.get(id = userId)
            
            if not user:
                return redirect('forgot password')
                        
            valid = PasswordResetTokenGenerator().check_token(user, token)            
            if valid:
                user.set_password(password); 
                user.save(update_fields=['password'])
                return redirect('student login')
            else:
                return redirect('forgot password')
        else:
            messages.error(request, "Password doesn't match")
            return redirect('reset password', uid = uid, token = token)
        
    return render(request, "resetPassword.html")

def changePassword(request):
    """Provides the functionality to the user to change the password by first taking in the old password and checking if that's correct then saving the new password in the database

    Args:
        request (HttpRequest): incoming HTTP request from the client 

    Returns:
        HttpResponse: Renders a HTML response initially, incase of no errors it redirects user to the home page 
    """
    if request.method == 'POST':
        user = request.user
        oldPassword = request.POST.get('oldPassword')
        newPassword = request.POST.get('newPassword')
        
        if user.check_password(oldPassword):
            user.set_password(newPassword)
            user.save(update_fields=['password'])
            update_session_auth_hash(request, user)
            messages.success(request, "Password Changed Successfully ")
            return redirect("home")
    return render(request, "changepassword.html")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------View Functions related to Student's Interaction-----------------------------------------------------------------------------------------------------------------------------------------

def home(request):
    """ If the user is admin it shows stats like no. of students, courses, HODs and departments by sending the data in context, 
    and if the user is student then it shows stats like full name, branch, year, semester , active courses, courses passed or failed, 
    also this function shows a greeting message and continous running date and time for both admin or student. 

    Args:
        request (HttpRequest): incoming HTTP request from the client

    Returns:
         HttpResponse: renders the HTML response and if user is already registered then redirects the user to home page
    """
    user = request.user
    
    firstName = user.first_name
    todayDate = datetime.now().strftime("%Y-%m-%d")
    
    if user.is_superuser:
        courseCount = len(courses.objects.all().values_list('id', flat=True))
        hodCount = len(courses.objects.values_list('HOD', flat=True).distinct())
        studentCount = len(students.objects.all().values_list('id', flat=True))
        deptCount = len(courses.objects.values_list('department', flat=True).distinct())
        
        context = {
            'courseCount':courseCount,
            'hodCount':hodCount,
            'studentCount':studentCount,
            'deptCount':deptCount,
        }
        
    else:
        studentInstance = students.objects.filter(student_id = user.id).first()
        branch = studentInstance.branch
        year = studentInstance.yos
        semester = studentInstance.semester
    
        passCount = len(enrollment.objects.filter(student_id = studentInstance.id, status = "pass").values_list("course_id", flat=True))
        failCount = len(enrollment.objects.filter(student_id = studentInstance.id, status = "fail").values_list("course_id", flat=True))
        activeCount = len(enrollment.objects.filter(student_id = studentInstance.id, status = "ongoing").values_list("course_id", flat=True))
        context = {
            'passCount':passCount,
            'failCount':failCount,
            'activeCount':activeCount,
            'branch':branch,
            'year':year,
            'semester':semester, 
        }
    
    context.update({'firstName':firstName, 'todayDate':todayDate})
    
    
    return render(request, "home.html", context)


def studentDetails(request):
    """Shows all the Profile details of the student as well as the admin depending upon the user 

    Args:
        request (HttpRequest): incoming HTTP request from the client

    Returns:
        HttpResponse: Renders the HTML response 
    """
    user = request.user
    if not user.is_superuser:
        studentInstance = students.objects.get(student = user.id)
        context = {
            'studentData': {
            'firstName': user.first_name,
            'lastName': user.last_name, 
            'email': user.email,
            'fatherName': studentInstance.fatherName, 
            'motherName': studentInstance.motherName,
            'contact': studentInstance.contact,
            'dob': studentInstance.dob,
            'branch': studentInstance.branch,
            'yos': studentInstance.yos,
            'address': studentInstance.address,
            'semester':studentInstance.semester,
            }
        }
        return render(request, "profile.html", context)
    
    else:
        dateJoined = user.date_joined.strftime("%Y-%m-%d")
        context = {
            'adminData':{
                'firstName':user.first_name, 
                'lastName':user.last_name, 
                'email':user.email, 
                'date_joined':dateJoined
            }
        }
        return render(request, "adminProfile.html", context)

def editStudentDetails(request):
    """Enables the students to change their details except fields like branch, year, dob, semester 

    Args:
        request (HttpRequest): incoming HTTP request from the client

    Returns:
        HttpResponse: Renders the HTML response initially then after saving the changes redirects the student to Profile page where details are visible 
    """
    user = request.user
    studentInstance = students.objects.get(student = user.id)
    context = {
        'studentData': {
        'firstName': user.first_name,
        'lastName': user.last_name, 
        'email': user.email,
        'fatherName': studentInstance.fatherName, 
        'motherName': studentInstance.motherName,
        'contact': studentInstance.contact,
        'dob': studentInstance.dob,
        'branch': studentInstance.branch,
        'yos': studentInstance.yos,
        'semester': studentInstance.semester,
        'address': studentInstance.address
       }
    }
    
    if request.method == 'POST':
        inputData = request.POST
        user.first_name = inputData.get('firstName')
        user.last_name = inputData.get('lastName')
        user.email = inputData.get('email')
        studentInstance.fatherName = inputData.get('fatherName')
        studentInstance.motherName = inputData.get('lastName')
        studentInstance.contact = inputData.get('contact')
        studentInstance.address = inputData.get('address')
        
        user.save()
        studentInstance.save()
        messages.success(request, "Changes made successfully")
        return redirect("student profile")
    return render(request, "editProfile.html", context)

def studentCourses(request):
    """Shows the students list of their courses and provides a filter option to see the courses with status like ongoing, pass or fail

    Args:
        request (HttpRequest): incoming HTTP request from the client

    Returns:
        HttpResponse: Renders the HTML response
    """
    user = request.user
    
    studentInstance = students.objects.get(student_id = user.id)
    filterData = request.GET.get('filter', "All")
    
    if filterData != 'All':
        courseIdList = enrollment.objects.filter(student_id = studentInstance.id, status = filterData).values_list('course_id', flat=True)
    
    else:
        courseIdList = enrollment.objects.filter(student_id = studentInstance.id).values_list('course_id', flat=True)
            
    courseData = []
    
    for id in courseIdList:
        enrollmentInstance = enrollment.objects.get(course_id = id, student_id = studentInstance.id)
        courseInstance = courses.objects.get(id = id)
        courseDict = {
            'name': courseInstance.name,
            'department': courseInstance.department,
            'HOD': courseInstance.HOD, 
            'status':enrollmentInstance.status.upper()
        }
        courseData.append(courseDict)
        
    context = {
        'courseData':courseData
    }
    
    return render(request, "myCourses.html", context)

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------View functions based on Admin's interaction---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def studentsList(request):
    """Shows the list of students 

    Args:
        request (HttpRequest): incoming HTTP request from the client

    Returns:
        HttpResponse: Renders the HTML response
    """
    studentsQs = students.objects.select_related('student').all().values_list('id','branch', 'yos','student__first_name', 'student__last_name', 'student__email', 'semester')
    
    studentsData = []
    count = 0
    for std in studentsQs:
        count += 1
        userDict = {
            'id': std[0],
            'firstName': std[3],
            'lastName': std[4],
            'email': std[5],
            'branch': std[1],
            'yos': std[2],
            'semester':std[6],
        }
        studentsData.append(userDict)
        
    context = {
        'studentsData': studentsData,
        'count': count
    }
    return render(request, "studentsList.html", context)

def editStudentProfile(request, id):
    """Provides the functionality to admin to change the profile details of any student 

    Args:
        request (HttpRequest): incoming HTTP request from the client
        id (int): student id whose details needs to be updated 

    Returns:
        HttpResponse: Renders the HTML response and after editing redirectes to students list url
    """
    studentInstance = students.objects.get(id = id)
    userInstance = User.objects.get(id = studentInstance.student_id)

    data = {
        'firstName':userInstance.first_name,
        'lastName':userInstance.last_name,
        'email':userInstance.email,
        'active':  userInstance.is_active,
        'fatherName': studentInstance.fatherName,
        'motherName': studentInstance.motherName,
        'contact': studentInstance.contact,
        'dob': studentInstance.dob,
        'address': studentInstance.address,
        'branch': studentInstance.branch,
        'yos': studentInstance.yos,
        'semester':studentInstance.semester,
    }
    
    if request.method == "POST":
        if request.POST.get('action') == 'delete':
            userInstance.delete()
            studentInstance.delete()
            
        else:
            inputData = request.POST
            userInstance.first_name = inputData.get('firstName')
            userInstance.last_name = inputData.get('lastName')
            userInstance.email = inputData.get('email')
            userInstance.is_active = inputData.get('active')
            studentInstance.fatherName = inputData.get('fatherName')
            studentInstance.motherName = inputData.get('lastName')
            studentInstance.contact = inputData.get('contact')
            studentInstance.address = inputData.get('address')
            studentInstance.dob = inputData.get('dob')
            studentInstance.yos = inputData.get('yos')
            studentInstance.branch = inputData.get('branch')
            studentInstance.semester = inputData.get('semester')
        
            userInstance.save()
            studentInstance.save()
        return redirect("students list")
    
    return render(request, "editStudentProfile.html", data)

def courseList(request):
    """Shows the List of all the courses 

    Args:
        request (HttpRequest): incoming HTTP request from the client

    Returns:
        HttpResponse: Renders the HTML response and after editing redirectes to students list url
    """
    courseQs = courses.objects.all()
    
    if request.method == "GET":
        search = request.GET.get('search')
        if search:
            courseQs = courses.objects.filter(Q(name__icontains = search) | Q(HOD__icontains = search) | Q(department__icontains = search))
            
    pageInstance = Paginator(courseQs, 10)
    pageNum = request.GET.get('page', 1)
    
    context = {
        'courseQs':pageInstance.get_page(pageNum)
    }
            
    return render(request, "courseList.html", context)

def editCourses(request, id):
    """Provides the functionality to edit the course details or removing a course from the Database

    Args:
        request (HttpRequest): incoming HTTP request from the client
        id (int): course id

    Returns:
        HttpResponse: Renders the HTML response and after editing redirectes to course list url
    """
    course = courses.objects.get(id = id)
    
    context = {
        'name': course.name,
        'dept': course.department,
        'HOD': course.HOD,
        'enrolled': course.enrolled_students,
        'year': course.year,
        'semester':course.semester,
    }
    
    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            course.delete()
        else:
            data = request.POST
            course.name = data.get('name')
            course.department = data.get('dept')
            course.HOD = data.get('HOD')
            course.enrolled_students = data.get('enrolled')
            course.year = data.get('year')
            course.semester = data.get('semester')
            course.save()
        
        return redirect('courses')
        
    return render(request, "editCourses.html", context)


def editStudentCourses(request, id):
    """Provides the functionality to change the status of any course student is enrolled in 

    Args:
        request (HttpRequest): incoming HTTP request from the client
        id (int): student's id

    Returns:
        HttpResponse: Renders the HTML response and after editing renders the same page either with success message or error message 
    """
    if request.method == "POST":
        updatedData = request.POST
        
        ifInvalid = False
        
        for key, value in updatedData.items():

            if not key.startswith('status_'):
                pass
            else:
                _, courseid = map(str, key.split("_"))
                courseid = int(courseid)
                
                courseInstance = courses.objects.get(id = courseid)
                enrollmentInstance = enrollment.objects.get(course_id = courseid, student_id = id)
                
                oldStatus = enrollmentInstance.status
                value = value.strip().lower()
                
                if value != oldStatus:
                    if value == "ongoing":
                        courseInstance.enrolled_students += 1
                        enrollmentInstance.status = value
                
                    elif value == "pass":
                        courseInstance.enrolled_students -= 1
                        enrollmentInstance.status = value
                
                    elif value == "fail":
                        courseInstance.enrolled_students -= 1
                        enrollmentInstance.status = value
                    
                    else:
                        ifInvalid = True
                        storage = messages.get_messages(request)
                        storage.used = True
                        
                        messages.error(request, "Please Provide a valid value for the status")
                        break
                    
                courseInstance.save()
                enrollmentInstance.save()
        
        if not ifInvalid:
            storage = messages.get_messages(request)
            storage.used = True
            messages.success(request, "Successfully Updated")   
    
    courseIdList = enrollment.objects.filter(student_id = id).values_list('course_id', flat=True)
    
    courseData = []
    
    for courseId in courseIdList:
        enrollmentInstance = enrollment.objects.get(course_id = courseId, student_id = id)
        courseInstance = courses.objects.get(id = courseId)
        courseDict = {
            'id':courseId,
            'name': courseInstance.name,
            'department': courseInstance.department,
            'HOD': courseInstance.HOD, 
            'status':enrollmentInstance.status
        }
        courseData.append(courseDict)
        
    context = {
        'courseData':courseData
    }
    
    return render(request, "editStudentCourse.html", context)