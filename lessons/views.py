from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Max
from courses.models import Course
from enrollments.models import Enrollment
from .models import Lesson


@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.course
    
    # Check if user is enrolled (for students) or is the instructor
    if request.user.is_student():
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).exists()
        
        if not is_enrolled:
            messages.error(request, 'You must enroll in this course to access lessons.')
            return redirect('courses:course_detail', pk=course.pk)
    
    # Get all lessons for navigation
    lessons = course.lessons.all()
    current_lesson_index = list(lessons).index(lesson)
    previous_lesson = lessons[current_lesson_index - 1] if current_lesson_index > 0 else None
    next_lesson = lessons[current_lesson_index + 1] if current_lesson_index < len(lessons) - 1 else None
    
    return render(request, 'lessons/lesson_detail.html', {
        'lesson': lesson,
        'course': course,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'lessons': lessons
    })


@login_required
@user_passes_test(lambda u: u.is_instructor())
def lesson_create(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, instructor=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        video_url = request.POST.get('video_url')
        video_file = request.FILES.get('video_file')
        text_content = request.POST.get('text_content')
        lesson_file = request.FILES.get('lesson_file')
        order = request.POST.get('order', 0)
        
        if title:
            lesson = Lesson.objects.create(
                title=title,
                course=course,
                video_url=video_url if video_url else None,
                video_file=video_file,
                text_content=text_content,
                lesson_file=lesson_file,
                order=int(order) if order else 0
            )
            messages.success(request, 'Lesson created successfully!')
            return redirect('lessons:lesson_detail', pk=lesson.pk)
        else:
            messages.error(request, 'Title is required.')
    
    # Get the next order number
    max_order = course.lessons.aggregate(Max('order'))['order__max'] or 0
    next_order = max_order + 1
    
    return render(request, 'lessons/lesson_create.html', {
        'course': course,
        'next_order': next_order
    })


@login_required
@user_passes_test(lambda u: u.is_instructor())
def lesson_edit(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, course__instructor=request.user)
    
    if request.method == 'POST':
        lesson.title = request.POST.get('title')
        lesson.video_url = request.POST.get('video_url')
        lesson.text_content = request.POST.get('text_content')
        lesson.order = int(request.POST.get('order', 0))
        
        if 'video_file' in request.FILES:
            lesson.video_file = request.FILES['video_file']
        
        if 'lesson_file' in request.FILES:
            lesson.lesson_file = request.FILES['lesson_file']
        
        lesson.save()
        messages.success(request, 'Lesson updated successfully!')
        return redirect('lessons:lesson_detail', pk=lesson.pk)
    
    return render(request, 'lessons/lesson_edit.html', {'lesson': lesson})


@login_required
@user_passes_test(lambda u: u.is_instructor())
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, course__instructor=request.user)
    course = lesson.course
    
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully!')
        return redirect('courses:course_detail', pk=course.pk)
    
    return render(request, 'lessons/lesson_delete.html', {'lesson': lesson})

