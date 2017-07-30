"""djsrv.views

Basic views providing the index and viewing pages.
"""

import getpass
import os
import socket

from django.shortcuts import render

import settings
import webnote

ARCHIVES = [
    ('/srv/content/notes', "Collection at /srv/content/notes"),
]

def index(request):
    """List the users on the host machine, and archives from a variable.

    """

    userspaces = []
    prefix = None

    for user in os.listdir('/home'):
        dirname = os.path.join('/home', user, 'www')
        if os.path.isdir(dirname):
            userspaces.append((user, user))
            prefix = '/' + user
    
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

        'navtemplate': 'nav_page.html',
        'HOST_DATA': settings.HOST_DATA,
        'breadcrumbs': breadcrumbs,

        'archives': ARCHIVES,
        'userspaces': userspaces,
    }
    
    return render(request, template, context)


def page(request, url):
    """Display a requested page.."""

    template = 'page.html'
    docroot = None
    prefix = None
                           
    breadcrumbs = [
        ('/', 'HOME'),
    ]

#   Process the URL
    bits = url.split('/')
    address = None

    dirname = os.path.join('/home', bits[0], 'www')

    if os.path.isdir(dirname):
        docroot = dirname
        prefix = '/' + bits[0]
        if len(bits) == 1:
            address = None
        elif len(bits) > 1:
            bits.pop(0)
            address = '/'.join(bits)
        print "BITS", bits

    else:
        for archive in ARCHIVES:
            if '/' + url == archive[0]:
                docroot = archive[0]
                address = None
                prefix = archive[0]
            elif archive[0] in '/' + url:
                docroot = archive[0]
                address = '/' + url.replace(docroot, '')

    print "STATS", docroot, address, prefix
    page = webnote.page.Page(docroot, address=address, prefix=prefix)

    title = 'A page at ' + page.title()
    breadcrumbs.extend(page.breadcrumbs())
    
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
        'navtemplate': 'nav_page.html',

        'HOST_DATA': settings.HOST_DATA,
    }
    
    return render(request, template, context)


