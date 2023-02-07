from django import forms

class KanjiForm(forms.Form):
	content=forms.CharField(widget=forms.Textarea)
