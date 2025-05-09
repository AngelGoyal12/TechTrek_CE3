from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        input_formats=['%Y-%m-%d'],
        required=False
    )
    
   
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='user'
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2',
            'bio', 'phone_number', 'address', 'date_of_birth', 'user_type'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'bio':
                field.widget.attrs['rows'] = 3

    def save(self, commit=True):
        user = super().save(commit=False)
        
        user.user_type = self.cleaned_data['user_type']
        if commit:
            user.save()
        return user
    

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'bio',
            'phone_number', 'address', 'date_of_birth'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'bio':
                field.widget.attrs['rows'] = 3