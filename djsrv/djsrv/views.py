"""djsrv.views

Basic views providing the index and viewing pages.
"""

import datetime
import getpass
import os
import pytz
import socket

from django.shortcuts import render, redirect

import forms
import settings
import webnote

# (url_prefix, docroot, link text).
ARCHIVES = [
    (
        '/manual', os.path.join(settings.STATICFILES_DIRS[0], 'manual'),
        "Webnote manual and test pages"
    ),

    (
        '/ruapehu', os.path.join(settings.STATICFILES_DIRS[0], 'ruapehu'),
        "Notes held on the ruapehu server.",
    ),
]


def index(request):
    """List the users on the host machine, and archives from the ARCHIVES
    variable.

    """

    userspaces = []
    baseurl = None

    for user in os.listdir('/home'):
        dirname = os.path.join('/home', user, 'www')
        if os.path.isdir(dirname):

            userspaces.append(('/home/' + user, user))
            baseurl = '/home/' + user

    template = 'index.html'

    title = "Webnote server at " + settings.HOST_DATA['hostname']
    index = webnote.directory.Directory(settings.HOST_DATA['userdir'],
                                        baseurl=baseurl)

    breadcrumbs = [
        ('/webnote/', 'HOME'),
    ]

    context = {

        'title': title,
        'index': index,

        'stylesheets': {
            'app': None,
            'screen': 'css/screen.css',
            'printer': 'css/print.css',
        },

        'navtemplate': None,
        'HOST_DATA': settings.HOST_DATA,
        'breadcrumbs': breadcrumbs,

        'archives': ARCHIVES,
        'userspaces': userspaces,
    }

    return render(request, template, context)


def page(request, url, command=None):
    """Display a requested page.."""

    address = ''
    baseurl = None
    command_form = None
    content_form = None
    dc_form = None
    docroot = None
    formsOn = None
    navtemplate = None
    newfile_form = None
    page = None
    template = 'page.html'
    title = 'A page at some place'

    breadcrumbs = [
        ('/', 'HOME'),
    ]

#   Process the url: is is a username?
    bits = url.split('/')
    if bits[0] == 'home':
        dirname = os.path.join('/home', bits[1], 'www')

        if os.path.isdir(dirname):
            docroot = dirname
            bits.pop(0)
            baseurl = '/home/' + bits[0]
            if len(bits) == 1:
                address = ''
            elif len(bits) > 1:
                bits.pop(0)
                address = '/'.join(bits)

#   Or is it in the ARCHIVES list?
    else:
        url = '/' + url
        for archive in ARCHIVES:
            if url == archive[0]:
                docroot = archive[1]
                address = ''
                baseurl = archive[0]
            elif archive[0] in url:
                docroot = archive[1]
                address = url.replace(archive[0] + '/', '')
                baseurl = archive[0]

    if docroot:
#   Now try to find a page object from the docroot and address.
        try:
            page = webnote.page.Page(docroot, address=address, baseurl=baseurl)
            title = page.title
            breadcrumbs.extend(page.breadcrumbs())
            navtemplate = 'nav_page.html'

#   If a value for type is in the metadata, set a template for it.
#   This permits pages being displayed differently to galleries.
            if len(page.metadata.metadata['type']) > 0:
                if len(page.metadata.metadata['type'][0]) > 0:
                    template = page.metadata.metadata['type'][0] + '.html'

        except webnote.page.Page.DocrootNotFound:
            template = 'warning_NotArchive.html'

    if command == 'edit' or command == 'new':

        template = 'editpage.html'
        navtemplate = 'nav_editpage.html'
        formsOn = True

        formdata = page.formdata()
        sort = None
        if page.metadata.sort:
            sort = page.metadata.sort

        dc_form = forms.DublinCoreForm(initial=formdata)
        command_form = forms.CommandForm(initial=formdata)
        content_form = forms.ContentForm(initial=formdata)
        content_form.fields['content'].initial = page.filecontent

        if command == 'new':
            newfile_form = forms.NewfileForm()
            content_form = forms.ContentForm()
            command_form = forms.CommandForm()
            dc_form = forms.DublinCoreForm()
            content_form.fields['content'].initial = ""
            dc_form.fields['dc_creator'].initial = "M.G.Hutchinson"
            dc_form.fields['dc_format'].initial = "text/markup"
            dc_form.fields['dc_language'].initial = "en"

    else:
        breadcrumbs.append(('edit', 'edit this page'))
        breadcrumbs.append(('new', 'new page'))

    if request.POST:
        if 'newfilename' in request.POST.keys():

            address = os.path.join(
                address,
                request.POST['newfilename'].replace(' ', '_')
            )

            newfile_form.fields['newfilename'].initial = (
                request.POST['newfilename'])

            page = webnote.page.Page(
                docroot, address=address, baseurl=baseurl,
                data=request.POST,
            )
            page.save(request.POST, files=request.FILES)
            return redirect(os.path.join(baseurl, address))

        page.save(request.POST, files=request.FILES)
        # Is this necessary, given the save operation above?
        page = webnote.page.Page(docroot, address=address, baseurl=baseurl)

        command_form = forms.CommandForm(initial=request.POST)
        dc_form = forms.DublinCoreForm(initial=request.POST)
        content_form = forms.ContentForm(initial=request.POST)

    css_app =''
    css_screen = 'css/screen.css'
    css_printer = 'css/print.css'

    # This is tracking an error at startup.

    if page:
        if page.metadata.metadata['stylesheet']:
            if not page.metadata.metadata['stylesheet'][0] == 'normal':
                css_screen = 'css/' + page.metadata.metadata['stylesheet'][0]
                css_screen += '-screen.css'
                css_printer = 'css/' + page.metadata.metadata['stylesheet'][0]
                css_printer += '-printer.css'

    context = {
        'docroot': docroot,
        'address': address,
        'baseurl': baseurl,
        'title': title,
        'page': page,
        'url': url,

        'stylesheets': {
            'app': css_app,
            'screen': css_screen,
            'printer': css_printer,
        },

        'breadcrumbs': breadcrumbs,
        'navtemplate': navtemplate,

        'formsOn': formsOn,
        'content_form': content_form,
        'command_form': command_form,
        'dc_form': dc_form,
        'newfile_form': newfile_form,

        'archives': ARCHIVES,
        'HOST_DATA': settings.HOST_DATA,

    }

    if page:
        context['liststyle'] = page.metadata.liststyle()

    return render(request, template, context)


def picture(request, url, picid):

    template = 'picture.html'
    navtemplate = 'nav_picture.html'
    h1 = 'Picture file'
    dirpath = None
    docroot = None
    baseurl = None
    gpsform = None
    fileform = None
    formsOn = None
    filename = None
    picture = None

    warnings = []

    if picid[-1] == '/':
        picid = picid[:-1]

#   Process the address into a docroot.
    bits = url.split('/')

    if bits[0] == 'home':
        dirname = os.path.join('/home', bits[1], 'www')
        if os.path.isdir(dirname):
            docroot = dirname
            bits.pop(0)
            baseurl = '/home/' + bits[0]
            if len(bits) == 1:
                address = ''
            elif len(bits) > 1:
                bits.pop(0)
                address = '/'.join(bits)

    dirpath = os.path.join(docroot, address)

#   The parent is a Gallery object.
    parent = webnote.gallery.Gallery(
        docroot=docroot, baseurl=baseurl, address=address,
    )

#   Find the filename with extension, from the basename picture id
#   (picid).
    for f in parent.paired.model['pictures']:
        if picid in f:
            filename = os.path.join(dirpath, f)


    if filename:
        picture = webnote.picture.Picture(
            filename, docroot=docroot, baseurl=baseurl)
    else:
        warnings.append("No picture file found at " + picid)

    formsOn = True
    fileform = forms.FileForm()

    if request.POST:

        if request.POST['command'] == 'accession':
            warnings.extend(parent.accession_pictures())

        elif request.POST['command'] == 'correlate':
            gpsform = forms.GPSForm(request.POST)
            if gpsform.is_valid():

                pictime = picture.EXIFdatetime()
                gpstime = request.POST['gpstime']
                UTC = pytz.timezone('UTC')
                gpstime = datetime.datetime.strptime(
                    request.POST['gpstime'],
                    "%Y-%m-%d %H:%M:%S",
                )

                tzoffset = request.POST['tzoffset']

                warnings.extend(parent.process_gps(pictime, gpstime, tzoffset))

        elif request.POST['command'] == 'upload':

            if request.FILES:
                fname = str(request.FILES['filename'])
                filepath = os.path.join(
                    picture.parent.dirpath, fname
                )

                f = request.FILES['filename']

                with open(filepath, 'wb') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)

                warnings.append("Uploading file " + fname)

        parent = webnote.gallery.Gallery(
            docroot=docroot, baseurl=baseurl, address=address,
        )
        picture = webnote.picture.Picture(
            filename, docroot=docroot, baseurl=baseurl)

#   Determine if accession and gps forms sre necessary.
    accession = False
    gpsform = False

    if not parent.processed():
        accession = True

    if picture:
        if not picture.GPSdatetime() and len(parent.gpxfiles()) > 0:
            gpsform = forms.GPSForm(initial={'tzoffset': '+1300'})

    if gpsform:
        accession = False

    context = {
        'h1': h1,
        'template': template,
        'navtemplate': navtemplate,
        'stylesheets': {
            'app': None,
            'screen': 'css/screen.css',
            'printer': 'css/print.css',
        },
        'picture': picture,
        'accession': accession,
        'formsOn': formsOn,
        'fileform': fileform,
        'gpsform': gpsform,
        'warnings': warnings,


    }
    return render(request, template, context)
