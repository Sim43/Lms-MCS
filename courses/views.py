from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Course, Category
from accounts.models import User
from enrollments.models import Enrollment


def home(request):
    featured_courses = Course.objects.filter(is_published=True)[:6]
    categories = Category.objects.all()[:6]
    return render(request, 'courses/home.html', {
        'featured_courses': featured_courses,
        'categories': categories
    })


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if category:
        courses = courses.filter(category__name=category)
    
    if search:
        courses = courses.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(instructor__username__icontains=search)
        )
    
    categories = Category.objects.all()
    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'categories': categories,
        'selected_category': category,
        'search_query': search
    })


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk, is_published=True)
    is_enrolled = False
    
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, 
            course=course
        ).exists()
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled
    })


@login_required
@user_passes_test(lambda u: u.is_instructor())
def instructor_course_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        thumbnail = request.FILES.get('thumbnail')
        
        if title and description:
            course = Course.objects.create(
                title=title,
                description=description,
                instructor=request.user,
                thumbnail=thumbnail,
                category_id=category_id if category_id else None,
                is_published=True
            )
            messages.success(request, 'Course created successfully!')
            return redirect('courses:course_detail', pk=course.pk)
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    categories = Category.objects.all()
    return render(request, 'courses/course_create.html', {'categories': categories})


@login_required
@user_passes_test(lambda u: u.is_instructor())
def instructor_course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    
    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        category_id = request.POST.get('category')
        
        if category_id:
            course.category_id = category_id
        else:
            course.category = None
        
        if 'thumbnail' in request.FILES:
            course.thumbnail = request.FILES['thumbnail']
        
        course.save()
        messages.success(request, 'Course updated successfully!')
        return redirect('courses:course_detail', pk=course.pk)
    
    categories = Category.objects.all()
    return render(request, 'courses/course_edit.html', {
        'course': course,
        'categories': categories
    })


@login_required
@user_passes_test(lambda u: u.is_instructor())
def instructor_course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('dashboards:instructor_dashboard')
    
    return render(request, 'courses/course_delete.html', {'course': course})


def custom_404(request, exception):
    return render(request, 'courses/404.html', status=404)


def custom_500(request):
    return render(request, 'courses/500.html', status=500)

