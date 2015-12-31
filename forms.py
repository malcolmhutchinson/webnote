"""Provide Django forms for common features in the webnote application.
"""

from django import forms
import settings

rights = []

for license in sorted(settings.LICENSES.keys()):
    rights.append((license, license))

    

class PageMetadataForm(forms.Form):
    dc_title = forms.CharField(
        label='title', required=False)
    dc_creator = forms.CharField(
        label='Author (semicolon separated)', required=False)
    dc_date = forms.DateField(
        label='date', required=False)
    dc_subject = forms.CharField(
        label='subject (comma separated)', max_length=255, required=False)
    dc_description = forms.CharField(
        label='description', widget=forms.Textarea, required=False)
    dc_contributor = forms.CharField(
        label='contributors', max_length=255, required=False)
    dc_coverage = forms.CharField(
        label='location', max_length=255, required=False)
    dc_rights = forms.ChoiceField(
        label='rights', choices=rights, required=False)
    dc_source = forms.CharField(
        label='source', max_length=255, required=False)
    dc_type = forms.ChoiceField(
        label='type', choices=settings.DOCTYPE, required=False)
    dc_publisher = forms.CharField(
        label='publisher', max_length=255, required=False)
    doc_status = forms.ChoiceField(
        label='status', choices=settings.PAGE_STATUS, required=False)
    deny = forms.CharField(
        label='deny', max_length=255, required=False)
    allow = forms.CharField(
        label='allow', max_length=255, required=False)

class PageEditForm(forms.Form):
    filecontent = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 15,}))

