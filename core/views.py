from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .decorators import admin_required, student_required, teacher_required
from .forms import (
    AdminLoginForm,
    AttendanceForm,
    GradeForm,
    PaymentAddForm,
    PaymentForm,
    ScheduleForm,
    SearchFilterForm,
    SpecialNumberForm,
    StudentForm,
    TeacherForm,
)
from .models import (
    AdminProfile,
    Attendance,
    Grade,
    GradeLevel,
    Payment,
    PaymentStatus,
    Schedule,
    Section,
    Student,
    Teacher,
)
from .throttle import is_login_throttled, record_login_attempt


def clear_session_role(request):
    """مسح بيانات الدور من الجلسة."""
    for key in ('role', 'teacher_id', 'teacher_name', 'student_id', 'student_name', 'pending_admin_number'):
        request.session.pop(key, None)


def home(request):
    if request.method == 'POST':
        if is_login_throttled(request):
            messages.error(request, 'تم تجاوز عدد محاولات تسجيل الدخول. حاول لاحقاً.')
            return render(request, 'home.html', {'form': SpecialNumberForm()})

        form = SpecialNumberForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data['special_number'].strip()

            admin = AdminProfile.objects.filter(special_number=number).first()
            if admin:
                request.session['pending_admin_number'] = number
                record_login_attempt(request, number, successful=True)
                return redirect('admin_login')

            teacher = Teacher.objects.filter(special_number=number, is_deleted=False).first()
            if teacher:
                clear_session_role(request)
                request.session['role'] = 'teacher'
                request.session['teacher_id'] = teacher.id
                request.session['teacher_name'] = teacher.name
                record_login_attempt(request, number, successful=True)
                return redirect('teacher_dashboard')

            student = Student.objects.filter(special_number=number, is_deleted=False).first()
            if student:
                clear_session_role(request)
                request.session['role'] = 'student'
                request.session['student_id'] = student.id
                request.session['student_name'] = student.name
                record_login_attempt(request, number, successful=True)
                return redirect('student_dashboard')

            record_login_attempt(request, number, successful=False)
            messages.error(request, 'الرقم المميز غير موجود. تحقق من الرقم وحاول مرة أخرى.')
    else:
        form = SpecialNumberForm()

    return render(request, 'home.html', {'form': form})


def admin_login(request):
    pending = request.session.get('pending_admin_number')
    if not pending:
        return redirect('home')

    if not AdminProfile.objects.filter(special_number=pending).exists():
        request.session.pop('pending_admin_number', None)
        return redirect('home')

    if request.method == 'POST':
        if is_login_throttled(request):
            messages.error(request, 'تم تجاوز عدد محاولات تسجيل الدخول. حاول لاحقاً.')
            return render(request, 'admin_login.html', {'form': AdminLoginForm()})

        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                AdminProfile.objects.get(special_number=pending, user=user)
            except AdminProfile.DoesNotExist:
                record_login_attempt(request, pending, successful=False)
                messages.error(request, 'هذا الحساب غير مرتبط بالرقم المميز.')
                return render(request, 'admin_login.html', {'form': AdminLoginForm()})
            clear_session_role(request)
            login(request, user)
            request.session['role'] = 'admin'
            record_login_attempt(request, pending, successful=True)
            return redirect('admin_dashboard')
        record_login_attempt(request, pending, successful=False)
        messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
    else:
        form = AdminLoginForm()

    return render(request, 'admin_login.html', {'form': form})


def logout_view(request):
    logout(request)
    clear_session_role(request)
    return redirect('home')


# ─── لوحة المدير ───────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    teachers_count = Teacher.objects.filter(is_deleted=False).count()
    students_count = Student.objects.filter(is_deleted=False).count()
    sections_count = Student.objects.filter(is_deleted=False).values('grade_level', 'section').distinct().count()
    pending_payments = Payment.objects.filter(status=PaymentStatus.PENDING).count()

    return render(request, 'admin/dashboard.html', {
        'teachers_count': teachers_count,
        'students_count': students_count,
        'sections_count': sections_count,
        'pending_payments': pending_payments,
    })


@admin_required
def admin_teachers(request):
    qs = Teacher.objects.filter(is_deleted=False)
    q = request.GET.get('q', '').strip()
    subject = request.GET.get('subject', '')

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(special_number__icontains=q))
    if subject:
        qs = qs.filter(subject=subject)

    subjects = Teacher.objects.filter(is_deleted=False).values_list('subject', flat=True).distinct()
    filter_form = SearchFilterForm(request.GET or None, subjects=subjects)

    paginator = Paginator(qs, 9)
    page = request.GET.get('page')
    teachers = paginator.get_page(page)

    form = TeacherForm()
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الأستاذ بنجاح.')
            return redirect('admin_teachers')

    return render(request, 'admin/teachers.html', {
        'teachers': teachers,
        'form': form,
        'filter_form': filter_form,
        'q': q,
    })


@admin_required
@require_POST
def admin_teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk, is_deleted=False)
    teacher.is_deleted = True
    teacher.save()
    messages.success(request, f'تم حذف الأستاذ {teacher.name} (حذف ناعم).')
    return redirect('admin_teachers')


@admin_required
def admin_students(request):
    qs = Student.objects.filter(is_deleted=False)
    q = request.GET.get('q', '').strip()
    grade_level = request.GET.get('grade_level', '')

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(special_number__icontains=q))
    if grade_level:
        qs = qs.filter(grade_level=grade_level)

    filter_form = SearchFilterForm(request.GET or None, subjects=[])
    paginator = Paginator(qs, 9)
    page = request.GET.get('page')
    students = paginator.get_page(page)

    form = StudentForm()
    edit_student = None
    edit_id = request.GET.get('edit')

    if edit_id:
        edit_student = get_object_or_404(Student, pk=edit_id, is_deleted=False)

    if request.method == 'POST':
        if 'edit_id' in request.POST:
            edit_student = get_object_or_404(Student, pk=request.POST['edit_id'], is_deleted=False)
            form = StudentForm(request.POST, instance=edit_student)
        else:
            form = StudentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ بيانات الطالب بنجاح.')
            return redirect('admin_students')

    return render(request, 'admin/students.html', {
        'students': students,
        'form': form,
        'filter_form': filter_form,
        'q': q,
        'edit_student': edit_student,
    })


@admin_required
@require_POST
def admin_student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk, is_deleted=False)
    student.is_deleted = True
    student.save()
    messages.success(request, f'تم حذف الطالب {student.name} (حذف ناعم).')
    return redirect('admin_students')


@admin_required
def admin_schedule(request):
    qs = Schedule.objects.select_related('teacher')
    grade_level = request.GET.get('grade_level', '')
    section = request.GET.get('section', '')

    if grade_level:
        qs = qs.filter(grade_level=grade_level)
    if section:
        qs = qs.filter(section=section)

    filter_form = SearchFilterForm(request.GET or None, subjects=[])
    form = ScheduleForm()

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الحصة بنجاح.')
            return redirect('admin_schedule')

    return render(request, 'admin/schedule.html', {
        'schedules': qs,
        'form': form,
        'filter_form': filter_form,
    })


@admin_required
def admin_teacher_schedule_search(request):
    teacher_name = request.GET.get('teacher_name', '').strip()
    schedules = Schedule.objects.select_related('teacher')
    if teacher_name:
        schedules = schedules.filter(teacher__name__icontains=teacher_name)

    return render(request, 'admin/teacher_schedule.html', {
        'schedules': schedules,
        'teacher_name': teacher_name,
    })


@admin_required
def admin_grades(request):
    qs = Grade.objects.select_related('student')
    section = request.GET.get('section', '')
    if section:
        qs = qs.filter(section=section)

    filter_form = SearchFilterForm(request.GET or None, subjects=[])
    form = GradeForm()

    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تسجيل العلامة بنجاح.')
            return redirect('admin_grades')

    return render(request, 'admin/grades.html', {
        'grades': qs,
        'form': form,
        'filter_form': filter_form,
    })


@admin_required
def admin_attendance(request):
    qs = Attendance.objects.select_related('student')
    section = request.GET.get('section', '')
    if section:
        qs = qs.filter(section=section)

    filter_form = SearchFilterForm(request.GET or None, subjects=[])
    form = AttendanceForm()

    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تسجيل الحضور بنجاح.')
            return redirect('admin_attendance')

    return render(request, 'admin/attendance.html', {
        'attendances': qs,
        'form': form,
        'filter_form': filter_form,
    })


@admin_required
def admin_payments(request):
    qs = Payment.objects.select_related('student')
    form = PaymentForm()
    add_form = PaymentAddForm()
    selected_payment = None

    payment_id = request.GET.get('add_to')
    if payment_id:
        selected_payment = get_object_or_404(Payment, pk=payment_id)

    if request.method == 'POST':
        if 'payment_id' in request.POST:
            payment = get_object_or_404(Payment, pk=request.POST['payment_id'])
            add_form = PaymentAddForm(request.POST)
            if add_form.is_valid():
                amount = add_form.cleaned_data['amount']
                payment.paid_amount += Decimal(str(amount))
                if payment.paid_amount > payment.total_amount:
                    payment.paid_amount = payment.total_amount
                payment.save()
                payment.update_status()
                messages.success(request, 'تم إضافة الدفعة بنجاح.')
                return redirect('admin_payments')
        else:
            form = PaymentForm(request.POST)
            if form.is_valid():
                payment = form.save(commit=False)
                payment.save()
                payment.update_status()
                messages.success(request, 'تم تسجيل الدفعة بنجاح.')
                return redirect('admin_payments')

    return render(request, 'admin/payments.html', {
        'payments': qs,
        'form': form,
        'add_form': add_form,
        'selected_payment': selected_payment,
    })


# ─── لوحة الأستاذ (قراءة فقط) ─────────────────────────────

@teacher_required
def teacher_dashboard(request):
    teacher_id = request.session.get('teacher_id')
    teacher = get_object_or_404(Teacher, pk=teacher_id, is_deleted=False)
    schedules = Schedule.objects.filter(teacher=teacher).order_by('day', 'time')

    return render(request, 'teacher/dashboard.html', {
        'teacher': teacher,
        'schedules': schedules,
    })


# ─── لوحة الطالب (قراءة فقط - من الجلسة فقط) ──────────────

@student_required
def student_dashboard(request):
    student_id = request.session.get('student_id')
    student = get_object_or_404(Student, pk=student_id, is_deleted=False)

    schedules = Schedule.objects.filter(
        grade_level=student.grade_level,
        section=student.section,
    ).select_related('teacher').order_by('day', 'time')

    grades = Grade.objects.filter(student=student).order_by('-date')
    attendances = Attendance.objects.filter(student=student).order_by('-date')
    payments = Payment.objects.filter(student=student)

    return render(request, 'student/dashboard.html', {
        'student': student,
        'schedules': schedules,
        'grades': grades,
        'attendances': attendances,
        'payments': payments,
    })
