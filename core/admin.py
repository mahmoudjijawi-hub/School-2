from django.contrib import admin

from .models import (
    AdminProfile,
    Attendance,
    Grade,
    LoginAttempt,
    Payment,
    Schedule,
    Student,
    Teacher,
)

admin.site.register(AdminProfile)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Schedule)
admin.site.register(Grade)
admin.site.register(Attendance)
admin.site.register(Payment)
admin.site.register(LoginAttempt)
