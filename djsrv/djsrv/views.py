"""djsrv.views

Basic views providing the index and viewing pages.
"""

import getpass
import os
import socket

from django.shortcuts import render

import settings
import webnote

def index(request):
    """Show the user's web folder."""

    template = 'index.html'

    title = "Webnote server at " + settings.HOST_DATA['hostname']
    index = webnote.directory.Directory(settings.HOST_DATA['userdir'])    
    
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
    }
    
    return render(request, template, context)


def page(request, url):
    """Display a requested page.."""

    template = 'page.html'

    levels = url.split('/')
    i = 0
    link = ''
    breadcrumbs = [
        ('/webnote/', 'HOME'),
    ]

    for level in levels:
        link += '/' + levels[i]
        breadcrumbs.append((link, level))
        i += 1
    
    page = webnote.page.Page(
        settings.HOST_DATA['userdir'],
        address=url,
        prefix='/webnote'
    )

    title = 'A page at ' + page.title

    print "HERE", breadcrumbs
    context = {

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


