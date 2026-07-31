def user_display(request):
    """معلومات العرض للمستخدم الحالي في القوالب."""
    display_name = ''
    role = request.session.get('role', '')

    if request.user.is_authenticated:
        display_name = request.user.get_full_name() or request.user.username
    elif role == 'teacher':
        display_name = request.session.get('teacher_name', 'أستاذ')
    elif role == 'student':
        display_name = request.session.get('student_name', 'طالب')

    return {
        'display_name': display_name,
        'user_role': role,
    }


def request_helpers(request):
    """مساعدات للقوالب (مثل الحفاظ على query string للبروكسي)."""
    qs = request.META.get('QUERY_STRING', '')
    return {
        'query_suffix': f'?{qs}' if qs else '',
        'form_action': request.get_full_path(),
    }
