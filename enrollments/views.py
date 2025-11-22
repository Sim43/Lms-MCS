from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course
from .models import Enrollment


@login_required
def enroll(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, is_published=True)
    
    if request.user.is_instructor():
        messages.error(request, 'Instructors cannot enroll in courses.')
        return redirect('courses:course_detail', pk=course.pk)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', pk=course.pk)
    
    # Create enrollment
    Enrollment.objects.create(student=request.user, course=course)
    messages.success(request, f'Successfully enrolled in {course.title}!')
    
    return render(request, 'enrollments/enrollment_success.html', {'course': course})


@login_required
def unenroll(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    
    if enrollment:
        enrollment.delete()
        messages.success(request, f'Successfully unenrolled from {course.title}.')
    else:
        messages.error(request, 'You are not enrolled in this course.')
    
    return redirect('dashboards:student_dashboard')

