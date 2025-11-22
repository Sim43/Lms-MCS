from django import template
import re

register = template.Library()


@register.filter
def youtube_embed(url):
    """Convert YouTube URL to embed format"""
    if not url:
        return ''
    
    # Extract video ID from various YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f'https://www.youtube.com/embed/{video_id}'
    
    # If already in embed format, return as is
    if 'youtube.com/embed/' in url:
        return url
    
    # If no match, return original URL
    return url

