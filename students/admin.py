from django.contrib import admin
from students.models import students, enrollment, courses

admin.site.register(students)
admin.site.register(enrollment)
admin.site.register(courses)


