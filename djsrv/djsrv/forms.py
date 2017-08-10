# Forms for the inplimentation of webnote.

from django import forms

class ContentForm(forms.Form):
    content = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 80,}))


    
class DublinCoreForm(forms.Form):
    dc_contributor = forms.CharField(max_length=255, label='contributer')
    dc_coverage = forms.CharField(max_length=255, label='location')
    dc_creator = forms.CharField(max_length=255, label='author')
    dc_date = forms.DateField(label='date')
    dc_description = forms.CharField(max_length=255, label='description')
    dc_format = forms.CharField(max_length=255, label='format')
    dc_language = forms.CharField(max_length=5, label='language')
    dc_publisher = forms.CharField(max_length=255, label='publisher')
    dc_relation = forms.CharField(max_length=255, label='relation')
    dc_rights = forms.CharField(max_length=255, label='rights')
    dc_source = forms.CharField(max_length=255, label='source')
    dc_subject = forms.CharField(max_length=255, label='keywords')
    dc_title = forms.CharField(max_length=255, label='title')
    dc_type = forms.CharField(max_length=255, label='type')




    
