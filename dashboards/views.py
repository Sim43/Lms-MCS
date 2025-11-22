from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from courses.models import Course
from enrollments.models import Enrollment
from lessons.models import Lesson


@login_required
def student_dashboard(request):
    if request.user.is_instructor():
        return redirect('dashboards:instructor_dashboard')
    
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    enrolled_courses = [enrollment.course for enrollment in enrollments]
    
    return render(request, 'dashboards/student_dashboard.html', {
        'enrolled_courses': enrolled_courses,
        'enrollments': enrollments
    })


@login_required
@user_passes_test(lambda u: u.is_instructor())
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user).prefetch_related('lessons')
    total_students = Enrollment.objects.filter(course__instructor=request.user).values('student').distinct().count()
    total_enrollments = Enrollment.objects.filter(course__instructor=request.user).count()
    
    return render(request, 'dashboards/instructor_dashboard.html', {
        'courses': courses,
        'total_students': total_students,
        'total_enrollments': total_enrollments
    })

