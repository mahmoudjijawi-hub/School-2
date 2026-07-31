from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),

    # لوحة المدير
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/teachers/', views.admin_teachers, name='admin_teachers'),
    path('admin-dashboard/teachers/<int:pk>/delete/', views.admin_teacher_delete, name='admin_teacher_delete'),
    path('admin-dashboard/students/', views.admin_students, name='admin_students'),
    path('admin-dashboard/students/<int:pk>/delete/', views.admin_student_delete, name='admin_student_delete'),
    path('admin-dashboard/schedule/', views.admin_schedule, name='admin_schedule'),
    path('admin-dashboard/schedule/teacher-search/', views.admin_teacher_schedule_search, name='admin_teacher_schedule_search'),
    path('admin-dashboard/grades/', views.admin_grades, name='admin_grades'),
    path('admin-dashboard/attendance/', views.admin_attendance, name='admin_attendance'),
    path('admin-dashboard/payments/', views.admin_payments, name='admin_payments'),

    # لوحة الأستاذ
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),

    # لوحة الطالب - بدون id في الرابط
    path('student/', views.student_dashboard, name='student_dashboard'),
]
