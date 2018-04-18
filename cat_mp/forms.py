from django import forms

class ImageForm(forms.Form):
    sess_key = forms.CharField(max_length=128)
    title = forms.CharField(max_length=200)
    content = forms.CharField(max_length=1024)
    album_id = forms.CharField(max_length=128)
    index = forms.IntegerField()
    fpath =  forms.FileField()
