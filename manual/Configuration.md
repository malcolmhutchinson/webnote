Configuring your webnote installation
=====================================

The webnote Django project should arrive pre-configured to scan the
`/home/` directory for user directories containing a `www` folder. At
least, those the user running the django server has the access
privileges to see.

So, if you are running the project in a Django development server, it
should, at least, find your own `~/home/www/` folder. If this doesn't
exist, the first thing you should do is create it:

    $ cd ~/
    $ mkdir www
    $ chmod 755 www

Webnote will assume the contents of this folder is an _archive_
containing files which conform to the simple syntax. It will find all
the page files in there and list them on the home page.

Now, create a symlink to your www folder in the static files folder,
within the Django project filespace. If you have set it up according
to the installation instructions, it will be something like this:

    $ cd ~/dev/webnote/code/djsrv/static
    $ mkdir home
    $ ln -s ~/www home/malcolm

The structure of the `staic/` folder should reflect the URLs you use
to address your pages. The default is to refer to user `malcolm` in
the url as:

    localhost:8000/home/malcolm/

Therefore, the `static/` folder should contain the directory
`home/`. This is where you put symlinks to user www directories.


