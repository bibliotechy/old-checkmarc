__author__ = 'libcbn'

from django import forms

class MarcUploadForm(forms.Form):
    filename = forms.FileField()


    #marcfield = forms.CharField(max_length=5)