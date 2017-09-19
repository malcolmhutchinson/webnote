"""djsrv.views

Basic views providing the index and viewing pages.
"""

import getpass
import os
import socket

from django.shortcuts import render, redirect

import forms
import settings
import webnote

# (url prefix, docroot, link text).
ARCHIVES = [
    ('/manual', os.path.join(settings.STATICFILES_DIRS[0], 'manual'),
     "Webnote manual and test pages"
    ),

    ('/ruapehu', os.path.join(settings.STATICFILES_DIRS[0], 'ruapehu'),
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

#   Now try to find a page object from the docroot and address.
    try:
        page = webnote.page.Page(docroot, address=address, baseurl=baseurl)
        title = page.title
        breadcrumbs.extend(page.breadcrumbs())
        navtemplate = 'nav_page.html'
    except webnote.page.Page.DocrootNotFound:
        template = 'warning_NotArchive.html'

    if command == 'edit' or command == 'new':

        template = 'editpage.html'
        navtemplate = 'nav_editpage.html'

        formdata = page.metadata.formdata()
        sort = None
        if page.metadata.sort:
            sort = page.metadata.sort

        dc_form = forms.DublinCoreForm(initial=formdata)
        command_form = forms.CommandForm(initial=formdata)
        content_form = forms.ContentForm()
        content_form.fields['content'].initial = page.filecontent

        if command == 'new':
            newfile_form = forms.NewfileForm()
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
        page = webnote.page.Page(docroot, address=address, baseurl=baseurl)

        command_form = forms.CommandForm(initial=formdata)
        dc_form = forms.DublinCoreForm(initial=page.metadata.formdata())
        content_form.fields['content'].initial = page.filecontent


    context = {
        'docroot': docroot,
        'address': address,
        'baseurl': baseurl,
        'title': title,
        'page': page,
        'url': url,

        'stylesheets': {
            'app': None,
            'screen': 'css/screen.css',
            'printer': 'css/print.css',
        },

        'breadcrumbs': breadcrumbs,
        'navtemplate': navtemplate,

        'content_form': content_form,
        'command_form': command_form,
        'dc_form': dc_form,
        'newfile_form': newfile_form,

        'archives': ARCHIVES,
        'HOST_DATA': settings.HOST_DATA,

    }

    return render(request, template, context)
