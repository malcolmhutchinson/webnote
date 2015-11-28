"""Provide Django forms for common features in the webnote application.
"""

from django import forms
import settings

rights = []

for license in settings.LICENSES.keys():
    rights.append(('license', 'license'))

    

class PageForm(forms.Form):
    dc_title = forms.CharField(
        label='title')
    dc_creator = forms.CharField(
        label='Author (semicolon separated)')
    dc_date = forms.DateField(
        label='date')
    dc_subject = forms.CharField(
        label='subject (comma separated)', max_length=255)
    dc_description = forms.CharField(
        label='description', widget=forms.Textarea)
    dc_contributor = forms.CharField(
        label='contributors', max_length=255)
    dc_coverage = forms.CharField(
        label='location', max_length=255)
    dc_rights = forms.ChoiceField(
        label='rights', choices=rights)
    dc_source = forms.CharField(
        label='source', max_length=255)
    dc_type = forms.ChoiceField(
        label='type', choices=settings.DOCTYPE)
    dc_publisher = forms.CharField(
        label='type', max_length=255)
    doc_status = forms.ChoiceField(
        label='status', choices=settings.PAGE_STATUS)
    deny = forms.CharField(
        label='deny', max_length=255)
    allow = forms.CharField(
        label='allow', max_length=255)
    
