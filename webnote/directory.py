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

    The attribute prefix is used to construct urls.

    """

    directory = None
    model = None
    prefix = None
    sort = None

    def __init__(self, directory, prefix=None, sort=True):

        if not os.path.isdir(directory):
            raise self.ParseDirNotFound(directory)

        if prefix:
            self.prefix = prefix

        self.directory = directory
        self.sort = sort
        self.model = self.parse_directory(directory)

    class ParseDirNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    def __unicode__(self):
        return self.directory

    def parse_directory(self, directory):
        """Return a dictionary containing lists of files by type.

        It looks for keys in the settings.SUFFIX variable. The output
        dictionary will have elemements corresponding to the keys of
        this dictionary. It will also contain elements "dirs",
        "hidden" and "all".

        Hidden files start with a period. Temporary files end with a
        tilde.
        """

        if not os.path.isdir(directory):
            raise self.ParseDirNotFound(directory)

        output = {
            'dirs': [],
            'hidden': [],
            'temp': [],
            'unknown': [],
        }

        for key in settings.SUFFIX:
            output[key] = []

        if self.sort:
            listing = sorted(os.listdir(directory))
        else:
            listing = os.listdir(directory)

        for item in listing:
            if item[0] == '.':
                output['hidden'].append(item)

            elif item[-1] == '~':
                output['temp'].append(item)

            elif os.path.isdir(os.path.join(directory, item)):
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

    def get_figs(self):
        if self.model['figs']:
            return self.model['figs']
        return []

    def link_self(self, prefix):

        link = os.path.join(prefix, self.directory)
        text = self.clean_name()
        return (link, text)

    def clean_name(self):

        steps = self.directory.split('/')
        last = steps.pop()

        name = last.replace('_', '')

        if last == 'www':
            name = '/home/' + getpass.getuser() + '/www/'
            
        return name

    def link_all(self, prefix):
        """Return a list of (link, text) tuples identifying all files."""

        targets = []

        for item in self.model['all']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def link_data(self, prefix):
        """Return a list of (link, text) tuples identifying data files."""

        targets = []

        for item in self.model['data']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def link_docs(self, prefix):
        """Return a list of (link, text) tuples identifying document files."""

        targets = []

        for item in self.model['docs']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def link_figs(self, prefix):
        """Return a list of (link, text) tuples identifying figure files."""

        targets = []

        for item in self.model['figs']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def link_hidden(self, prefix):
        """Return a list of (link, text) tuples identifying hidden files."""

        targets = []

        for item in self.model['hidden']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def link_html(self, prefix):
        """Return a list of (link, text) tuples identifying all html files."""

        targets = []

        for item in self.model['html']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def link_image(self, prefix):
        """Return a list of (link, text) tuples identifying image files."""

        images = []

        for item in self.model['img_hires']:
            link = os.path.join(prefix, item)
            text = item
            images.append((link, text))

        return images

    def link_meta(self, prefix):
        """Return a list of (link, text) tuples identifying meta files."""

        targets = []

        for item in self.model['']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def link_temp(self, prefix):
        """Return a list of (link, text) tuples identifying temporary files."""

        targets = []

        for item in self.model['']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def link_text(self, prefix):
        """Return a list of (link, text) tuples identifying text files."""

        targets = []

        for item in self.model['text']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def link_pages(self, prefix, suffix=False):
        """DEPRECIATED"""
        return self.list_pages(prefix, suffix)

    def link_unknown(self, prefix):
        """Return a list of (link, text) tuples identifying  files."""

        targets = []

        for item in self.model['unknown']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets

    def list_pages(self, prefix=None, suffix=False):
        """Return a list of (link, text) tuples identifying page files."""

        targets = []

        if not prefix:
            if self.prefix:
                prefix = self.prefix
            else:
                prefix = ''

        for item in self.model['page']:
            (basename, ext) = os.path.splitext(item)
            link = os.path.join(prefix, basename) + '/'
            if suffix:
                text = item
            else:
                text = basename.replace('_', ' ')

            targets.append((link, text))

        return targets

