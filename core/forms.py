from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import (
    Attendance,
    AttendanceStatus,
    Grade,
    GradeLevel,
    Payment,
    PaymentType,
    Schedule,
    Section,
    Student,
    Teacher,
)


class SpecialNumberForm(forms.Form):
    special_number = forms.CharField(
        label='الرقم المميز',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'أدخل الرقم المميز',
            'autofocus': True,
        }),
    )


class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'اسم المستخدم'}),
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'كلمة المرور'}),
    )


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'special_number', 'gender', 'phone', 'subject', 'cv']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'special_number': forms.TextInput(attrs={'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'subject': forms.TextInput(attrs={'class': 'form-input'}),
            'cv': forms.FileInput(attrs={'class': 'form-input'}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'special_number', 'student_phone', 'parent_phone',
            'address', 'notes', 'grade_level', 'section',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'special_number': forms.TextInput(attrs={'class': 'form-input'}),
            'student_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'grade_level': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
        }


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['day', 'grade_level', 'section', 'subject', 'teacher', 'room', 'time']
        widgets = {
            'day': forms.Select(attrs={'class': 'form-select'}),
            'grade_level': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-input'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'room': forms.TextInput(attrs={'class': 'form-input'}),
            'time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = Teacher.objects.filter(is_deleted=False)


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['exam_name', 'date', 'section', 'student', 'score', 'note']
        widgets = {
            'exam_name': forms.TextInput(attrs={'class': 'form-input'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'note': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_deleted=False)


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'section', 'student', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_deleted=False)
        self.fields['status'].choices = AttendanceStatus.choices


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'payment_type', 'total_amount', 'paid_amount']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_deleted=False)


class PaymentAddForm(forms.Form):
    """إضافة مبلغ على دفعة موجودة."""
    amount = forms.DecimalField(
        label='المبلغ المضاف',
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
    )


class SearchFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.HiddenInput())
    subject = forms.ChoiceField(required=False, label='المادة', widget=forms.Select(attrs={'class': 'form-select filter-auto'}))
    grade_level = forms.ChoiceField(required=False, label='المرحلة', widget=forms.Select(attrs={'class': 'form-select filter-auto'}))
    section = forms.ChoiceField(required=False, label='الشعبة', widget=forms.Select(attrs={'class': 'form-select filter-auto'}))
    teacher_name = forms.CharField(required=False, label='اسم الأستاذ', widget=forms.TextInput(attrs={'class': 'form-input filter-auto', 'placeholder': 'بحث باسم الأستاذ'}))

    def __init__(self, *args, **kwargs):
        subjects = kwargs.pop('subjects', [])
        super().__init__(*args, **kwargs)
        self.fields['subject'].choices = [('', 'كل المواد')] + [(s, s) for s in subjects]
        self.fields['grade_level'].choices = [('', 'كل المراحل')] + list(GradeLevel.choices)
        self.fields['section'].choices = [('', 'كل الشعب')] + list(Section.choices)
