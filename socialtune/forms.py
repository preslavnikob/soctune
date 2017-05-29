from __future__ import absolute_import, unicode_literals
from django import forms
from django.forms import  PasswordInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from socialtune.models import   Users


class UserCreateForm(UserCreationForm):
    username = forms.CharField(label= "Your Username       ")
    password1 = forms.CharField(label="Your Password       ")
    password2 = forms.CharField(label="Repeat Your Password")
    email = forms.EmailField(label=   "Email Address       ")
    insta_login = forms.CharField(max_length=200)
    insta_password = forms.CharField(max_length=200)
    # twitter_login = forms.CharField(max_length=200)
    # twitter_password=forms.CharField(max_length=200)

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email", "insta_login", "insta_password")
    def save(self, commit=True):
        if not commit:
            raise NotImplementedError("Can't create User and UserProfile without database save")
        user = super(UserCreateForm, self).save(commit=True)
        user.email = self.cleaned_data["email"]
        user.save()
        user_profile = Users(user=user, insta_login=self.cleaned_data['insta_login'],
                             insta_password=self.cleaned_data['insta_password'],
                             # twitter_login=self.cleaned_data['twitter_login'],
                             # twitter_password=self.cleaned_data['twitter_password']
                             )
        user_profile.save()

        return user_profile


class InstaLoginChange(forms.Form):
    insta_login = forms.CharField(max_length=200)
    insta_password = forms.CharField(widget=forms.PasswordInput())

    def save(self):
        return self.cleaned_data['insta_login'],self.cleaned_data['insta_password']