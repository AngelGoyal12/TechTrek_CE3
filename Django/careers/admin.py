from django.contrib import admin
from .models import JobApplication

# admin.site.register(JobApplication)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'email', 'experience', 'applied_on')
    list_filter = ('position', 'experience', 'applied_on')
    search_fields = ('name', 'email', 'position', 'cover_letter')
    date_hierarchy = 'applied_on'
    readonly_fields = ('applied_on',)
    
    fieldsets = (
        ('Applicant Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Job Details', {
            'fields': ('position', 'experience')
        }),
        ('Application Materials', {
            'fields': ('resume', 'portfolio', 'cover_letter')
        }),
        ('Metadata', {
            'fields': ('applied_on',)
        }),
    )
