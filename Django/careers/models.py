from django.db import models
from django.utils import timezone

class JobApplication(models.Model):
    """Model to store job applications"""
    EXPERIENCE_CHOICES = [
        ('1-2', '1-2 years'),
        ('3-5', '3-5 years'),
        ('5+', '5+ years'),
    ]
    
    position = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    experience = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES)
    resume = models.FileField(upload_to='resumes/')
    portfolio = models.URLField(blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    applied_at = models.DateTimeField(default=timezone.now)
    
    
    def __str__(self):
        return f"{self.name} - {self.position}"
    class Meta:
        ordering = ['-applied_at']