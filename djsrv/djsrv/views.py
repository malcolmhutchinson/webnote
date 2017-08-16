"""djsrv.views

Basic views providing the index and viewing pages.
"""

import getpass
import os
import socket

from django.shortcuts import render

import forms
import settings
import webnote

# (url prefix, docroot, link text).
ARCHIVES = [
    ('/notes', '/srv/content/notes', "Collection at /srv/content/notes"),
    ('/intranet', '/srv/content/intranet', "The old intranet"),
    ('/test', os.path.join(settings.STATICFILES_DIRS[0], 'test'),
     "Test archive"
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

    address = None
    baseurl = None
    content_form = None
    dc_form = None
    docroot = None
    navtemplate = None
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
                address = None
            elif len(bits) > 1:
                bits.pop(0)
                address = '/'.join(bits)
        
#   Or is it in the ARCHIVES list?
    else:
        url = '/' + url
        for archive in ARCHIVES:
            if url == archive[0]:
                docroot = archive[1]
                address = None
                baseurl = archive[0]
            elif archive[0] in url:
                docroot = archive[1]
                address = url.replace(archive[0] + '/', '')
                baseurl = archive[0]

    #print "DOCROOT", docroot
    #print "ADDRESS", address
    #print "BASEURL", baseurl


    try:
        page = webnote.page.Page(docroot, address=address, baseurl=baseurl)
        title = page.title
        breadcrumbs.extend(page.breadcrumbs())
        navtemplate = 'nav_page.html'
    except webnote.page.Page.DocrootNotFound:
        template = 'warning_NotArchive.html'   

    if command == 'edit':

        template = 'editpage.html'
        navtemplate = 'nav_editpage.html'

        dc_form = forms.DublinCoreForm(initial=page.metadata.formdata_dc())

        content_form = forms.ContentForm()
        content_form.fields['content'].initial = page.filecontent

    if request.POST:
        page.save(request.POST)
        page = webnote.page.Page(docroot, address=address, baseurl=baseurl)
        dc_form = forms.DublinCoreForm(initial=page.metadata.formdata_dc())
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
        'dc_form': dc_form,

        'archives': ARCHIVES,
        'HOST_DATA': settings.HOST_DATA,
        
    }

    return render(request, template, context)


