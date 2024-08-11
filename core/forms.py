# forms.py

from django import forms
from .models import Address
from django.contrib.auth.models import User
from django.core.validators import validate_email

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True, validators=[validate_email])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
 'first_name', 'last_name', 'email', 'address', 'address2', 
            'country', 'state', 'zip_code', 'message','default'
        ]
        # widgets = {
        #     'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John', 'id': 'firstName'}),
        #     'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doe', 'id': 'lastName'}),
        #     'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com', 'id': 'email'}),
        #     'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234 Main St', 'id': 'address'}),
        #     'address2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, studio, or floor', 'id': 'address2'}),
        #     'country': forms.Select(attrs={'class': 'form-select', 'id': 'country'}),
        #     'state': forms.Select(attrs={'class': 'form-select', 'id': 'state'}),
        #     'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12345', 'id': 'zip'}),
        #     'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Leave a message for us here', 'id': 'msj'}),
        #     'default': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'default'}),
        # }
class AddAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'first_name', 'last_name', 'email', 'address', 'address2', 
            'country', 'state', 'zip_code', 'message', 'default'
        ]