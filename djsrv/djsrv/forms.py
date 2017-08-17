# Forms for the inplimentation of webnote.

from django import forms

class ContentForm(forms.Form):
    content = forms.CharField(
        label='', required=False,
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 80,})
    )


class DublinCoreForm(forms.Form):
    filename = forms.FileField(required=False, label='Upload file')
    dc_title = forms.CharField(
        max_length=255, required=False, label='title')
    dc_creator = forms.CharField(
        max_length=255, required=False, label='author')
    dc_subject = forms.CharField(
        max_length=255, required=False, label='keywords')
    dc_coverage = forms.CharField(
        max_length=255, required=False, label='location')
    dc_date = forms.DateField(label='date', required=False)
    dc_description = forms.CharField(
        max_length=255, required=False, label='description')
    dc_contributor = forms.CharField(
        max_length=255, required=False, label='contributer')
    dc_format = forms.CharField(
        max_length=255, required=False, label='format')
    dc_language = forms.CharField(
        max_length=5, required=False, label='language')
    dc_publisher = forms.CharField(
        max_length=255, required=False, label='publisher')
    dc_relation = forms.CharField(
        max_length=255, required=False, label='relation')
    dc_rights = forms.CharField(
        max_length=255, required=False, label='rights')
    dc_source = forms.CharField(
        max_length=255, required=False, label='source')
    dc_type = forms.CharField(
        max_length=255, required=False, label='type')



    
