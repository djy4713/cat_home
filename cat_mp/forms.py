from django import forms

class ImageForm(forms.Form):
    sess_key = forms.CharField(max_length=128)
    title = forms.CharField(max_length=200)
    fpath =  forms.FileField()
