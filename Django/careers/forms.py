from django import forms
from .models import JobApplication

class JobApplicationForm(forms.ModelForm):
    """Form for job applications"""
    class Meta:
        model = JobApplication
        fields = ['position', 'name', 'email', 'phone', 'experience', 
                  'resume', 'portfolio', 'cover_letter']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['resume'].required = True
        
       
        self.fields['resume'].help_text = 'Upload your resume (PDF format only)'
        
    def clean_resume(self):
        """Validate that resume is a PDF file"""
        resume = self.cleaned_data.get('resume')
        if resume:
            file_ext = resume.name.split('.')[-1].lower()
            if file_ext != 'pdf':
                raise forms.ValidationError("Only PDF files are allowed for resumes.")
        return resume