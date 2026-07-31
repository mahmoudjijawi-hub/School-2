from django.contrib.auth.models import User
from django.db import models


class Gender(models.TextChoices):
    MALE = 'male', 'ذكر'
    FEMALE = 'female', 'أنثى'


class GradeLevel(models.TextChoices):
    FIRST = 'first', 'الأول'
    SECOND = 'second', 'الثاني'
    THIRD = 'third', 'الثالث'
    FOURTH = 'fourth', 'الرابع'


class Section(models.TextChoices):
    A = 'a', 'أ'
    B = 'b', 'ب'
    C = 'c', 'ج'


class DayOfWeek(models.TextChoices):
    SUNDAY = 'sunday', 'الأحد'
    MONDAY = 'monday', 'الاثنين'
    TUESDAY = 'tuesday', 'الثلاثاء'
    WEDNESDAY = 'wednesday', 'الأربعاء'
    THURSDAY = 'thursday', 'الخميس'
    FRIDAY = 'friday', 'الجمعة'
    SATURDAY = 'saturday', 'السبت'


class AttendanceStatus(models.TextChoices):
    PRESENT = 'present', 'حاضر'
    ABSENT = 'absent', 'غائب'


class PaymentType(models.TextChoices):
    FULL = 'full', 'دفعة كاملة'
    INSTALLMENT = 'installment', 'تقسيط'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'قيد التحصيل'
    COMPLETED = 'completed', 'مكتمل'


class AdminProfile(models.Model):
    """ربط المدير برقم مميز وحساب Django."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    special_number = models.CharField('الرقم المميز', max_length=20, unique=True)

    class Meta:
        verbose_name = 'مدير'
        verbose_name_plural = 'المدراء'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.special_number})'


class Teacher(models.Model):
    name = models.CharField('الاسم', max_length=150)
    special_number = models.CharField('الرقم المميز', max_length=20, unique=True)
    gender = models.CharField('الجنس', max_length=10, choices=Gender.choices)
    phone = models.CharField('الهاتف', max_length=20)
    subject = models.CharField('المادة', max_length=100)
    cv = models.FileField('السيرة الذاتية', upload_to='cvs/', blank=True, null=True)
    is_deleted = models.BooleanField('محذوف', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'أستاذ'
        verbose_name_plural = 'الأساتذة'
        ordering = ['name']

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField('الاسم', max_length=150)
    special_number = models.CharField('الرقم المميز', max_length=20, unique=True)
    student_phone = models.CharField('هاتف الطالب', max_length=20)
    parent_phone = models.CharField('هاتف الأهل', max_length=20)
    address = models.TextField('العنوان', blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    grade_level = models.CharField('المرحلة', max_length=20, choices=GradeLevel.choices)
    section = models.CharField('الشعبة', max_length=5, choices=Section.choices)
    is_deleted = models.BooleanField('محذوف', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'طالب'
        verbose_name_plural = 'الطلاب'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_grade_level_display_ar(self):
        return self.get_grade_level_display()

    def get_section_display_ar(self):
        return self.get_section_display()


class Schedule(models.Model):
    day = models.CharField('اليوم', max_length=15, choices=DayOfWeek.choices)
    grade_level = models.CharField('المرحلة', max_length=20, choices=GradeLevel.choices)
    section = models.CharField('الشعبة', max_length=5, choices=Section.choices)
    subject = models.CharField('المادة', max_length=100)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='الأستاذ', related_name='schedules')
    room = models.CharField('القاعة', max_length=50)
    time = models.TimeField('الساعة')

    class Meta:
        verbose_name = 'حصة'
        verbose_name_plural = 'البرنامج الدراسي'
        ordering = ['day', 'time']

    def __str__(self):
        return f'{self.get_day_display()} - {self.subject}'


class Grade(models.Model):
    exam_name = models.CharField('اسم المذاكرة', max_length=150)
    date = models.DateField('التاريخ')
    section = models.CharField('الشعبة', max_length=5, choices=Section.choices)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='الطالب', related_name='grades')
    score = models.DecimalField('العلامة', max_digits=5, decimal_places=2)
    note = models.TextField('ملاحظة', blank=True)

    class Meta:
        verbose_name = 'علامة'
        verbose_name_plural = 'العلامات'
        ordering = ['-date']

    def __str__(self):
        return f'{self.student.name} - {self.exam_name}: {self.score}'


class Attendance(models.Model):
    date = models.DateField('التاريخ')
    section = models.CharField('الشعبة', max_length=5, choices=Section.choices)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='الطالب', related_name='attendances')
    status = models.CharField('الحالة', max_length=10, choices=AttendanceStatus.choices)

    class Meta:
        verbose_name = 'حضور'
        verbose_name_plural = 'الحضور والغياب'
        ordering = ['-date']
        unique_together = ['date', 'student']

    def __str__(self):
        return f'{self.student.name} - {self.date} - {self.get_status_display()}'


class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='الطالب', related_name='payments')
    payment_type = models.CharField('نوع الدفعة', max_length=15, choices=PaymentType.choices)
    total_amount = models.DecimalField('المبلغ الكلي', max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField('المدفوع', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('الحالة', max_length=15, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'المدفوعات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.name} - {self.paid_amount}/{self.total_amount}'

    @property
    def remaining(self):
        return max(self.total_amount - self.paid_amount, 0)

    @property
    def progress_percent(self):
        if self.total_amount <= 0:
            return 0
        return min(int((self.paid_amount / self.total_amount) * 100), 100)

    def update_status(self):
        if self.paid_amount >= self.total_amount:
            self.status = PaymentStatus.COMPLETED
        else:
            self.status = PaymentStatus.PENDING
        self.save(update_fields=['status', 'updated_at'])


class LoginAttempt(models.Model):
    """تتبع محاولات تسجيل الدخول لتحديد بسيط (throttling)."""
    ip_address = models.GenericIPAddressField()
    identifier = models.CharField(max_length=100, blank=True)
    attempted_at = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)

    class Meta:
        ordering = ['-attempted_at']
