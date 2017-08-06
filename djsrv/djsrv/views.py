"""djsrv.views

Basic views providing the index and viewing pages.
"""

import getpass
import os
import socket

from django.shortcuts import render

import settings
import webnote

ARCHIVES2 = [
    ('/srv/content/notes', "Collection at /srv/content/notes"),
    ('/srv/content/intranet', "The old intranet"),
    ('/srv/content/test', "Test archive"),
]

# New format (not implemented yet)
# (url prefix, docroot, link text.
ARCHIVES = [
    ('/notes', '/srv/content/notes', "Collection at /srv/content/notes"),
    ('/intranet', '/srv/content/intranet', "The old intranet"),
    ('/test', '/srv/content/test', "Test archive"),
]

def edit(request):
    template = 'editpage.html'
    
    return render(request, template, context)


def index(request):
    """List the users on the host machine, and archives from the ARCHIVES
    variable.

    """

    userspaces = []
    prefix = None

    for user in os.listdir('/home'):
        dirname = os.path.join('/home', user, 'www')
        if os.path.isdir(dirname):
            
            userspaces.append(('/home/' + user, user))
            prefix = '/home/' + user
    
    template = 'index.html'

    title = "Webnote server at " + settings.HOST_DATA['hostname']
    index = webnote.directory.Directory(settings.HOST_DATA['userdir'],
                                        prefix=prefix)    
    
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


def page(request, url):
    """Display a requested page.."""

    page = None
    template = 'page.html'
    navtemplate = None
    docroot = None
    prefix = None
    title = 'A page at some place' 
                           
    breadcrumbs = [
        ('/', 'HOME'),
    ]

#   Process the URL
    address = None

#   Process the url: is is a username?
    bits = url.split('/')

    if bits[0] == 'home':
        dirname = os.path.join('/home', bits[1], 'www')
        if os.path.isdir(dirname):
            docroot = dirname
            bits.pop(0)
            prefix = '/home/' + bits[0] 
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
                prefix = archive[0]
            elif archive[0] in url:
                docroot = archive[1]
                address = url.replace(archive[0] + '/', '')
                prefix = archive[0]

    #print "DOCROOT", docroot
    #print "ADDRESS", address
    #print "PREFIX", prefix

    try:
        page = webnote.page.Page(docroot, address=address, prefix=prefix)
        title = page.title
        breadcrumbs.extend(page.breadcrumbs())
        navtemplate = 'nav_page.html'
    except webnote.page.Page.DocrootNotFound:
        template = 'warning_NotArchive.html'   
    
    context = {
        'docroot': docroot,
        'address': address,
        'prefix': prefix,
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

        'archives': ARCHIVES,
        'HOST_DATA': settings.HOST_DATA,
        
    }

    return render(request, template, context)


