from django import forms

class UploadFileForm(forms.Form):
    name = forms.CharField()
    type = forms.CharField()
    source = forms.CharField()
    extra = forms.CharField()
    file = forms.FileField()


class UploadTaskForm(forms.Form):
    name = forms.CharField()
    member = forms.CharField()
    sample = forms.CharField()
    engines = forms.CharField()