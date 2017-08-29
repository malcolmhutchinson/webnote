Download and install webnote
============================



The webnote software can be used in Python programs without a Django
installation. If this is your case, reading the
[Webnote architecture wiki](https://github.com/malcolmhutchinson/webnote/wiki/Webnote-architecture)
will explain how the various components can be used. The Python source
files for webnote classes are contained in the `webnote` folder.

Files for the sample Django implementation are held in the `djsrv`
folder.

If you are unfamiliar with Django, I recommend following the
[Django
tutorial](https://docs.djangoproject.com/en/dev/intro/tutorial01/).

Create a development directory:

    $ mkdir ~/dev/webnote
    $ cd ~/dev/webnote

Make a directory to hold the code under version control:

    $ mkdir code

Clone the code from github:

    $ git clone https://github.com/malcolmhutchinson/webnote.git code/

Install a virtual environment. 

    $ virtualenv env

You will have to install Django, and a number of other dependencies,
into the environment:

    $ source env/bin/activate
    (env) $ pip install django, markdown2, bs4

You will have to put the webnote package onto your path. I've done
this by placing a simlink in my virtual environment at

    $ ln -s ~/dev/webnote/code/webnote ~/dev/webnote/env/lib/python2.7/site-packages/webnote

Now, run the Django development server:

    (env) $ python code/djsrv/manage.py runserver

And point your browser at localhost, port 8000:

    http://localhost:8000/

You should see a page indexing pages in your own `~/www` folder, and a
list of other users (if any) on the system. This will index any folder
in `/home` which contains a folder called `www`.

In order to see your figures and image files displayed inline on pages
in the webserver, you will have to add a symlink in the Django
project's `static` folder:

    $ ln -s /home/malcolm/www ~/dev/webnote/code/djsrv/static/home/malcolm

The structure of folders and symlinks in `static/` should echo the url
structure. Since home folders are called with url's like :

    http://localhost:8000/home/malcolm/

There should be a folder `static/home/malcolm/`.
