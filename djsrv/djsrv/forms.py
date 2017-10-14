# Forms for the inplimentation of webnote.

from django import forms

LISTSTYLE = (
    ('default', 'default'),
    ('feature', 'feature'),
    ('short', 'short'),
    ('simple', 'simple'),
)

PAGETYPE = (
    ('gallery', 'gallery',),
    ('page', 'page'),
    (None, '-'),
)

SORT = (
    ('forward', 'forward'),
    ('reverse', 'reverse'),
)

STATUS = (
    ('draft', 'draft'),
    ('revision', 'revision'),
    ('complete', 'complete'),
    ('standing', 'standing'),
)



class CommandForm(forms.Form):
    sort = forms.ChoiceField(required=False, choices=SORT)
    liststyle = forms.ChoiceField(required=False, choices=LISTSTYLE)
    status = forms.ChoiceField(required=False, choices=STATUS)
    pagetype = forms.ChoiceField(required=False, choices=PAGETYPE)
    filename = forms.FileField(required=False, label='Upload file')


class ContentForm(forms.Form):
    
    dc_title = forms.CharField(
        max_length=255, required=False, label='title')
    dc_subject = forms.CharField(
        max_length=255, required=False, label='keywords')
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


class FileForm(forms.Form):
    filename = forms.CharField(max_length=255)
    filename = forms.FileField(required=False, label='Upload file')


class PictureForm(forms.Form):

    gpstime = forms.DateTimeField(required=False, label='GPS datetime')
    tzoffset = forms.IntegerField(required=False, label='Timezone offset (hrs)')

