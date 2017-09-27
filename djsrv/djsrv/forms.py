# Forms for the inplimentation of webnote.

from django import forms

LISTSTYLE = (
    ('simple', 'simple'),
    ('standard', 'standard'),
    ('feature', 'feature'),
    ('default', 'default'),
)

SORT = (
    ('forward', 'forward'),
    ('reversee', 'reverse'),
)

STATUS = (
    ('draft', 'draft'),
    ('revision', 'revision'),
    ('complete', 'complete'),
    ('standing', 'standing'),
)



class CommandForm(forms.Form):
    dc_title = forms.CharField(
        max_length=255, required=False, label='title')
    dc_subject = forms.CharField(
        max_length=255, required=False, label='keywords')
    sort = forms.ChoiceField(required=False, choices=SORT)
    liststyle = forms.ChoiceField(required=False, choices=LISTSTYLE)
    status = forms.ChoiceField(required=False, choices=STATUS)
    filename = forms.FileField(required=False, label='Upload file')


class ContentForm(forms.Form):
    
    dc_description = forms.CharField(
        max_length=255, required=False, label='description')
    content = forms.CharField(
        label='', required=False,
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 80,})
    )


class DublinCoreForm(forms.Form):
    dc_creator = forms.CharField(
        max_length=255, required=False, label='author')
    dc_date = forms.DateField(label='date', required=False)
    dc_coverage = forms.CharField(
        max_length=255, required=False, label='location')
    dc_type = forms.CharField(
        max_length=255, required=False, label='type')
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


class NewfileForm(forms.Form):
    newfilename = forms.CharField(max_length=255)
