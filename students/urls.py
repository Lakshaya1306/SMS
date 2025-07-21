from django.urls import path 
from students.views import registration, login, forgotPassword, resetPassword, changePassword, home, studentDetails, editStudentDetails, studentsList, editStudentProfile, courseList, editCourses, completeProfilePage, studentCourses, editStudentCourses, logout
urlpatterns = [
    path('registration/', registration, name="student registration"),
    path('login/', login, name = "student login"),
    path('logout/', logout, name = "logout"),
    path('home/', home, name = "home"),
    path('forgot_password/', forgotPassword, name = "forgot password"),
    path('reset_password/<str:uid>/<str:token>/', resetPassword, name = "reset password"),
    path('change_password/', changePassword, name = "change password"),
    path('profile/', studentDetails, name = "student profile"), 
    path('profile/edit_details', editStudentDetails, name = "edit details"),
    path('students_list/', studentsList, name = "students list"),
    path('students_list/<int:id>/', editStudentProfile, name = "edit profile"),
    path('edit_course/<int:id>/', editStudentCourses, name = "edit student course"),
    path('courses/', courseList, name = "courses"),
    path('courses/<int:id>/', editCourses, name ="edit course"),
    path('complete_profile/',completeProfilePage, name = "complete profile"),
    path('mycourses/', studentCourses, name = "my courses"),
]
