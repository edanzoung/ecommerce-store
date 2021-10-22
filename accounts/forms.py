from django import forms
from accounts.models import Account, UserProfile
#from django.contrib import messages

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'',
                                                                'class':'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':''}))
    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password','gender','country','state','city','quartier']
        
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError('Mot De Passe non identique')
        
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = ''
        self.fields['last_name'].widget.attrs['placeholder'] = ''
        self.fields['phone_number'].widget.attrs['placeholder'] = ''
        self.fields['email'].widget.attrs['placeholder'] = '' 
        self.fields['gender'].widget.attrs['placeholder'] = ''
        self.fields['country'].widget.attrs['placeholder'] = ''
        self.fields['state'].widget.attrs['placeholder'] = ''
        self.fields['city'].widget.attrs['placeholder'] = ''
        self.fields['quartier'].widget.attrs['placeholder'] = ''
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
            
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number','gender','country','state','city','quartier')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2','gender','country','state','city','quartier', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
