from django.db import models
from django.urls import reverse
from courses.models import Course


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or other video URL")
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    text_content = models.TextField(blank=True, help_text="Lesson text content")
    lesson_file = models.FileField(upload_to='lesson_files/', blank=True, null=True, help_text="PDF, DOCX, etc.")
    order = models.IntegerField(default=0, help_text="Order in which lesson appears")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('lessons:lesson_detail', kwargs={'pk': self.pk})

