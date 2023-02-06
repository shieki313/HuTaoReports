from django import forms
from django.core.exceptions import ValidationError

class TextForm(forms.Form):
    text = forms.CharField()
    search = forms.CharField()
    replace = forms.CharField()
    
class StatusForm(forms.Form):
    HP = forms.IntegerField(label="HP")
    Cr = forms.FloatField(label="会心率")
    Cd = forms.FloatField(label="会心ダメージ")

class ProcessImageForm(forms.Form):
    brightness = forms.IntegerField(label="UID")
