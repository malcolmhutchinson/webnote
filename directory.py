"""Classes implimenting the simple filesystem syntax.
"""

import os

import settings
from webnote import Webnote


class Directory(Webnote):
    """Provide directory services.

    Services include generating lists of files by type as (link, text)
    tuples. Has property attributes to provide lists of figures,
    hi-res images, documents and other files by type.

    """

    directory = None
    model = None
    sort = None

    def __init__(self, directory, sort=True):

        if not os.path.isdir(directory):
            raise self.ParseDirNotFound(directory)

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

    def _get_link(self):
        return self.directory

    link = property(_get_link)

    def _get_all(self):
        return self.model['all']

    allfiles = property(_get_all)

    def _get_data(self):
        return self.model['data']

    data = property(_get_data)

    def _get_dirs(self):
        return self.model['dirs']

    dirs = property(_get_dirs)

    def _get_docs(self):
        return self.model['docs']

    docs = property(_get_docs)

    def _get_figs(self):
        if self.model['figs']:
            return self.model['figs']
        return []

    figs = property(_get_figs)

    def _get_hidden(self):
        return self.model['hidden']

    hidden = property(_get_hidden)

    def _get_html(self):
        return self.model['html']

    html = property(_get_html)

    def _get_image(self):
        return self.model['image']

    image = property(_get_image)

    def _get_meta(self):
        return self.model['meta']

    meta = property(_get_meta)

    def _get_temp(self):
        return self.model['temp']

    temp = property(_get_temp)

    def _get_text(self):
        return self.model['text']

    text = property(_get_text)

    def _get_pages(self):
        return self.model['page']

    pages = property(_get_pages)

    def _get_unknown(self):
        return self.model['unknown']

    unknown = property(_get_unknown)

    def link_self(self, prefix):

        link = os.path.join(prefix, self.directory)
        text = self.clean_name()
        return (link, text)

    def clean_name(self):

        steps = self.directory.split('/')
        last = steps.pop()

        name = last.replace('_', '')

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
        """Return a list of (link, text) tuples identifying page files."""

        targets = []

        for item in self.model['page']:
            (basename, ext) = os.path.splitext(item)
            link = os.path.join(prefix, basename) + '/'
            if suffix:
                text = item
            else:
                text = basename.replace('_', ' ')

            targets.append((link, text))

        return targets

    def link_unknown(self, prefix):
        """Return a list of (link, text) tuples identifying  files."""

        targets = []

        for item in self.model['unknown']:
            link = os.path.join(prefix, item)
            text = item
            targets.append((link, text))

        return targets
