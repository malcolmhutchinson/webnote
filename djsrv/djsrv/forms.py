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

STYLESHEET = (
    ('normal', 'normal'),
    ('book', 'book'),
    ('letter', 'letter'),
    ('manuscript', 'manuscript'),
    ('typescript', 'typescript'),
)

TZOFFSET = (
    ('0000', '0000',),
    ('+1200', '+1200',),
    ('+1245', '+1245',),
    ('+1300', '+1300',),
)


class CommandForm(forms.Form):
    sort = forms.ChoiceField(required=False, choices=SORT)
    liststyle = forms.ChoiceField(required=False, choices=LISTSTYLE)
    stylesheet = forms.ChoiceField(required=False, choices=STYLESHEET)
    status = forms.ChoiceField(required=False, choices=STATUS)
    type = forms.ChoiceField(required=False, choices=PAGETYPE)
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
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 80, })
    )


class NewfileForm(forms.Form):

    newfilename = forms.CharField(label='Name', max_length=255)


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
    filename = forms.FileField(
        required=False, label='Upload file',
    )


class GPSForm(forms.Form):

    gpstime = forms.DateTimeField(label='GPS datetime')
    tzoffset = forms.ChoiceField(
        required=False, choices=TZOFFSET, label='Timezone offset (hrs)')
