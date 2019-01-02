"""Classes implimenting the simple filesystem syntax.
"""

import getpass
import os
import settings

from webnote import Webnote


class Directory(Webnote):
    """Provide directory services.

    Services include generating lists of files by type as (link, text)
    tuples. Has property attributes to provide lists of figures,
    hi-res images, documents and other files by type.

    The attribute baseurl is used to construct urls.

    """

    address = None
    dirpath = None
    model = None
    baseurl = None
    sort = None

    def __init__(self, dirpath, docroot=None, baseurl=None, sort=True):
        """Create a Directory object from a string path to directory.

        The address is computed by cutting the docroot from the dirpath.
        """

        if not os.path.isdir(dirpath):
            raise self.ParseDirNotFound(dirpath)

        if docroot:
            if docroot[-1] == '/':
                docroot = docroot[:-1]
            if dirpath == docroot:
                self.docroot = ''
                self.address = ''
            else:
                self.docroot = docroot

                self.address = dirpath.replace(docroot, '')

        if baseurl:
            self.baseurl = baseurl

        self.dirpath = dirpath
        self.sort = sort
        self.model = self._parse_directory(dirpath)

    class ParseDirNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    def __unicode__(self):
        return self.dirpath

    def _parse_directory(self, dirpath):
        """Return a dictionary containing lists of files by type.

        It looks for keys in the settings.SUFFIX variable. The output
        dictionary will have elemements corresponding to the keys of
        this dictionary. It will also contain elements "dirs",
        "hidden" and "all".

        Hidden files start with a period. Temporary files end with a
        tilde.
        """

        if not os.path.isdir(dirpath):
            raise self.ParseDirNotFound(dirpath)

        output = {
            'dirs': [],
            'hidden': [],
            'temp': [],
            'unknown': [],
        }

        for key in settings.SUFFIX:
            output[key] = []

        if self.sort:
            listing = sorted(os.listdir(dirpath))
        else:
            listing = os.listdir(dirpath)

        for item in listing:
            if item[0] == '.':
                output['hidden'].append(item)

            elif item[-1] == '~':
                output['temp'].append(item)

            elif os.path.isdir(os.path.join(dirpath, item)):
                output['dirs'].append(item)

            else:
                basename, ext = os.path.splitext(item)
                found = False
                for key in settings.SUFFIX:
                    if ext.lower() in settings.SUFFIX[key]:
                        output[key].append(item)
                        found = True
                if not found:
                    output['unknown'].append(item)

        output['all'] = listing

        return output

    def all_files(self, baseurl=None):
        """Return a list of (link, text) tuples identifying all files."""

        targets = []

        for item in self.model['all']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            targets.append((link, text))

        return targets

    def clean_name(self):

        steps = self.dirpath.split('/')
        last = steps.pop()

        name = last.replace('_', '')

        if last == 'www':
            name = '/home/' + getpass.getuser() + '/www/'

        return name

    def datafiles(self, baseurl=None):
        """Return a list of (link, text) tuples identifying data files."""

        targets = []

        for item in self.model['data']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            targets.append((link, text))

        return targets

    def documents(self, baseurl=None):
        """Return a list of (link, text) tuples identifying document files."""

        targets = []

        for item in self.model['docs']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            targets.append((link, text))

        return targets

    def figures(self, baseurl=''):
        """Return a list of (link, text) tuples identifying figure files."""

        targets = []

        if not baseurl:
            if self.baseurl:
                baseurl = self.baseurl

        for item in self.model['figures']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            targets.append((link, text))

        return targets

    def hiddenfiles(self, baseurl=None):
        """Return a list of (link, text) tuples identifying hidden files."""

        targets = []

        for item in self.model['hidden']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            targets.append((link, text))

        return targets

    def hiresimages(self, baseurl=None):
        """Return a list of (link, text) tuples identifying image files."""

        images = []

        for item in self.model['img_hires']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            images.append((link, text))

        return images

    def htmlfiles(self, baseurl=None):
        """Return a list of (link, text) tuples identifying all html files."""

        targets = []

        for item in self.model['html']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            targets.append((link, text))

        return targets

    def metafiles(self, baseurl=None):
        """Return a list of (link, text) tuples identifying meta files."""

        targets = []

        for item in self.model['']:
            link = os.path.join(baseurl, item)
            text = item
            targets.append((link, text))

        return targets

    def pages(self, baseurl=None, suffix=None):
        """Return a list of (link, text) tuples identifying page files."""

        targets = []
        address = ''
        if self.address:
            address = self.address

        if not baseurl:
            if self.baseurl:
                baseurl = os.path.join(self.baseurl, address)

            else:
                baseurl = ''

        for item in self.model['page']:
            (basename, ext) = os.path.splitext(item)
            link = os.path.join(baseurl, basename) + '/'
            if suffix:
                text = item
            else:
                text = basename.replace('_', ' ')

            targets.append((link, text))

        return targets

    def reference_text(self, text, baseurl=None):
        """Return an alterted text, and unreferenced figures.

        Return a tuple: reftext, unref_figs, using the
        reference_figures() method in the superclass. Requires only
        the text to be processed, if the directory object has been
        created with a baseurl.

        """
        reftext = text
        
        figures = []
        if not baseurl:
            baseurl = self.baseurl

        for t in self.figures():
            figures.append(t[0])

        reftext, unref_figs = self.reference_figures(text, baseurl, figures)
        
        return reftext, unref_figs

    def tempfiles(self, baseurl=None):
        """Return a list of (link, text) tuples identifying temporary files."""

        targets = []

        for item in self.model['']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            targets.append((link, text))

        return targets

    def textfiles(self, baseurl=None):
        """Return a list of (link, text) tuples identifying text files."""

        targets = []

        for item in self.model['text']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            targets.append((link, text))

        return targets

    def unknownfiles(self, baseurl=None):
        """Return a list of (link, text) tuples identifying  files."""

        targets = []

        for item in self.model['unknown']:
            link = os.path.join(baseurl, self.address, item)
            text = item
            targets.append((link, text))

        return targets
