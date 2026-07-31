from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, time

from core.models import (
    AdminProfile,
    Attendance,
    AttendanceStatus,
    DayOfWeek,
    Gender,
    Grade,
    GradeLevel,
    LoginAttempt,
    Payment,
    PaymentStatus,
    PaymentType,
    Schedule,
    Section,
    Student,
    Teacher,
)


class Command(BaseCommand):
    help = 'زرع بيانات تجريبية للعرض على العميل'

    def handle(self, *args, **options):
        self.stdout.write('جاري زرع البيانات التجريبية...')

        # مسح البيانات القديمة (اختياري للتجربة)
        LoginAttempt.objects.all().delete()
        Payment.objects.all().delete()
        Attendance.objects.all().delete()
        Grade.objects.all().delete()
        Schedule.objects.all().delete()
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        AdminProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # المدير
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'first_name': 'أحمد', 'last_name': 'المدير', 'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        AdminProfile.objects.get_or_create(
            user=admin_user,
            defaults={'special_number': '1001'},
        )

        # الأساتذة
        teachers_data = [
            {'name': 'محمد العلي', 'special_number': '2001', 'gender': Gender.MALE, 'phone': '0501111111', 'subject': 'رياضيات'},
            {'name': 'فاطمة السعيد', 'special_number': '2002', 'gender': Gender.FEMALE, 'phone': '0502222222', 'subject': 'لغة عربية'},
            {'name': 'خالد الحربي', 'special_number': '2003', 'gender': Gender.MALE, 'phone': '0503333333', 'subject': 'علوم'},
        ]
        teachers = []
        for t in teachers_data:
            teacher, _ = Teacher.objects.get_or_create(special_number=t['special_number'], defaults=t)
            teachers.append(teacher)

        # الطلاب
        students_data = [
            {'name': 'عبدالله محمد', 'special_number': '3001', 'student_phone': '0551111111', 'parent_phone': '0551111112', 'address': 'الرياض', 'grade_level': GradeLevel.FIRST, 'section': Section.A},
            {'name': 'نورة أحمد', 'special_number': '3002', 'student_phone': '0552222221', 'parent_phone': '0552222222', 'address': 'جدة', 'grade_level': GradeLevel.FIRST, 'section': Section.A},
            {'name': 'سعود خالد', 'special_number': '3003', 'student_phone': '0553333331', 'parent_phone': '0553333332', 'address': 'الدمام', 'grade_level': GradeLevel.SECOND, 'section': Section.B},
            {'name': 'ريم سعد', 'special_number': '3004', 'student_phone': '0554444441', 'parent_phone': '0554444442', 'address': 'مكة', 'grade_level': GradeLevel.SECOND, 'section': Section.B},
            {'name': 'فيصل عمر', 'special_number': '3005', 'student_phone': '0555555551', 'parent_phone': '0555555552', 'address': 'المدينة', 'grade_level': GradeLevel.THIRD, 'section': Section.C},
        ]
        students = []
        for s in students_data:
            student, _ = Student.objects.get_or_create(special_number=s['special_number'], defaults=s)
            students.append(student)

        # البرنامج الدراسي
        schedules_data = [
            {'day': DayOfWeek.SUNDAY, 'grade_level': GradeLevel.FIRST, 'section': Section.A, 'subject': 'رياضيات', 'teacher': teachers[0], 'room': 'قاعة 1', 'time': time(8, 0)},
            {'day': DayOfWeek.SUNDAY, 'grade_level': GradeLevel.FIRST, 'section': Section.A, 'subject': 'لغة عربية', 'teacher': teachers[1], 'room': 'قاعة 2', 'time': time(9, 30)},
            {'day': DayOfWeek.MONDAY, 'grade_level': GradeLevel.FIRST, 'section': Section.A, 'subject': 'علوم', 'teacher': teachers[2], 'room': 'مختبر 1', 'time': time(8, 0)},
            {'day': DayOfWeek.TUESDAY, 'grade_level': GradeLevel.SECOND, 'section': Section.B, 'subject': 'رياضيات', 'teacher': teachers[0], 'room': 'قاعة 3', 'time': time(10, 0)},
            {'day': DayOfWeek.WEDNESDAY, 'grade_level': GradeLevel.SECOND, 'section': Section.B, 'subject': 'لغة عربية', 'teacher': teachers[1], 'room': 'قاعة 2', 'time': time(8, 30)},
            {'day': DayOfWeek.THURSDAY, 'grade_level': GradeLevel.THIRD, 'section': Section.C, 'subject': 'علوم', 'teacher': teachers[2], 'room': 'مختبر 2', 'time': time(9, 0)},
        ]
        for sch in schedules_data:
            Schedule.objects.get_or_create(
                day=sch['day'], grade_level=sch['grade_level'], section=sch['section'],
                subject=sch['subject'], teacher=sch['teacher'], room=sch['room'], time=sch['time'],
            )

        # العلامات
        grades_data = [
            {'exam_name': 'مذاكرة الأول', 'date': date(2026, 1, 15), 'section': Section.A, 'student': students[0], 'score': Decimal('85.5'), 'note': 'أداء جيد'},
            {'exam_name': 'مذاكرة الأول', 'date': date(2026, 1, 15), 'section': Section.A, 'student': students[1], 'score': Decimal('92.0'), 'note': 'ممتاز'},
            {'exam_name': 'مذاكرة الثاني', 'date': date(2026, 2, 10), 'section': Section.B, 'student': students[2], 'score': Decimal('78.0'), 'note': ''},
            {'exam_name': 'مذاكرة الثاني', 'date': date(2026, 2, 10), 'section': Section.B, 'student': students[3], 'score': Decimal('88.5'), 'note': 'تحسن ملحوظ'},
        ]
        for g in grades_data:
            Grade.objects.get_or_create(
                exam_name=g['exam_name'], date=g['date'], student=g['student'],
                defaults={'section': g['section'], 'score': g['score'], 'note': g['note']},
            )

        # الحضور
        attendance_data = [
            {'date': date(2026, 3, 1), 'section': Section.A, 'student': students[0], 'status': AttendanceStatus.PRESENT},
            {'date': date(2026, 3, 1), 'section': Section.A, 'student': students[1], 'status': AttendanceStatus.PRESENT},
            {'date': date(2026, 3, 2), 'section': Section.A, 'student': students[0], 'status': AttendanceStatus.ABSENT},
            {'date': date(2026, 3, 2), 'section': Section.A, 'student': students[1], 'status': AttendanceStatus.PRESENT},
            {'date': date(2026, 3, 1), 'section': Section.B, 'student': students[2], 'status': AttendanceStatus.PRESENT},
            {'date': date(2026, 3, 1), 'section': Section.B, 'student': students[3], 'status': AttendanceStatus.ABSENT},
        ]
        for a in attendance_data:
            Attendance.objects.get_or_create(
                date=a['date'], student=a['student'],
                defaults={'section': a['section'], 'status': a['status']},
            )

        # المدفوعات
        payments_data = [
            {'student': students[0], 'payment_type': PaymentType.FULL, 'total_amount': Decimal('5000'), 'paid_amount': Decimal('5000'), 'status': PaymentStatus.COMPLETED},
            {'student': students[1], 'payment_type': PaymentType.INSTALLMENT, 'total_amount': Decimal('6000'), 'paid_amount': Decimal('3000'), 'status': PaymentStatus.PENDING},
            {'student': students[2], 'payment_type': PaymentType.INSTALLMENT, 'total_amount': Decimal('5500'), 'paid_amount': Decimal('2000'), 'status': PaymentStatus.PENDING},
            {'student': students[3], 'payment_type': PaymentType.FULL, 'total_amount': Decimal('5000'), 'paid_amount': Decimal('2500'), 'status': PaymentStatus.PENDING},
        ]
        for p in payments_data:
            Payment.objects.get_or_create(
                student=p['student'], payment_type=p['payment_type'],
                defaults={'total_amount': p['total_amount'], 'paid_amount': p['paid_amount'], 'status': p['status']},
            )

        self.stdout.write(self.style.SUCCESS('\nتم زرع البيانات التجريبية بنجاح!\n'))
        self.stdout.write('=' * 50)
        self.stdout.write(self.style.WARNING('بيانات الدخول التجريبية:'))
        self.stdout.write('=' * 50)
        self.stdout.write('\n【 المدير 】')
        self.stdout.write('  الرقم المميز: 1001')
        self.stdout.write('  اسم المستخدم: admin')
        self.stdout.write('  كلمة المرور: admin123')
        self.stdout.write('\n【 الأساتذة 】(الرقم المميز فقط)')
        self.stdout.write('  محمد العلي (رياضيات): 2001')
        self.stdout.write('  فاطمة السعيد (لغة عربية): 2002')
        self.stdout.write('  خالد الحربي (علوم): 2003')
        self.stdout.write('\n【 الطلاب 】(الرقم المميز فقط)')
        self.stdout.write('  عبدالله محمد: 3001')
        self.stdout.write('  نورة أحمد: 3002')
        self.stdout.write('  سعود خالد: 3003')
        self.stdout.write('  ريم سعد: 3004')
        self.stdout.write('  فيصل عمر: 3005')
        self.stdout.write('\n' + '=' * 50)
