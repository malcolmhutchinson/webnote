"""Classes interpreting the simple filesystem syntax.
"""

import os
import markdown2 as markdown

from directory import Directory
import settings
from metadata import Metadata
from webnote import Webnote


class Page(Webnote):
    """Compute metadata about a page within a simple syntax filesystem.

    This class computes data surrounding a page object, giving it
    context. It finds the parent, previous and next pages, the
    marked-up content of the text file, and a list of child pages if
    any exist.

    A page is a text or HTML file within the document root
    filesystem. It may have a directory with the same basename
    associated with it (the pared directory), which is where any child
    pages, and any images referred to in the text, will be found. It
    may also have a metadata file associated with it.


    ### Usage

        webnote.Page(docroot, address=None, prefix=None)

    Initialise with a docroot string, pointing to the root directory
    for an archive. If no address is supplied, it will look for a page
    called 'index'.

    The prefix it prepended to the link src value, providing a way of
    referencing local files with an URL.

    Provides the following attributes:

        title      A computed title for the page.
        content    Marked-up text content of the file.
        parent     Page object to the parent page.
        previous   Link tuple to the Previous page in a series.
        nextpage   Link tuple to the Next page in a series.
        siblings   List of link tuples to other pages in the same directory.
        children   List of link tuples to pages in the paired directory.

    A link tuple has the form (link, text), and is intended to go into
    a template like this:

        <a href ='{{ link }}'>{{ text }}</a>

    """

    docroot = None
    address = None
    prefix = None

    parent_dirname = None
    paired_dirname = None

    # These are stored webnote directory structures.
    parent_directory = None
    paired_directory = None

    # The name and contents of the target file.
    filename = None
    filecontent = None
    unref_figs = None

    # These are internal (link, text) tuples, and lists of same.
    _store_title = None
    _store_content = None
    _store_parent = None
    _store_files = None
    _store_children = None
    _store_siblings = None
    _store_previous = None
    _store_nextpage = None
    _store_unref_figs = None
    _store_documents = None

    warnings = []

    def __init__(self, docroot, address=None, prefix='/', staticroot=''):
        """Instantiating without an address will return the index file.

        Do the minimum necessary computations.
        - Set globals for input variables.
        - Determine the docroot exists. Exit with exception if not.
        - Compute the addressed file & read it.
        - Compute the parent and paired directories.
        - Create a Metadata object.

        Special case: no address = docroot index.

            Instantiate without an address, and it will default to the
            docroot index.

            This looks for a file called 'index' with one of the
            values in settings.SUFFIX['page']. If it doesn't find one,
            it addeds a line to the warnings list.

        """

        if not os.path.isdir(docroot):
            raise self.DocrootNotFound(docroot)

        self.warnings = []
        self.figs = None

        self.docroot = docroot
        if docroot[-1] != '/':
            self.docroot = docroot + '/'

        self.address = address
        if address and address[-1] == '/':
            self.address = address[:-1]

        self.staticroot = staticroot

        if prefix:
            self.prefix = prefix
        else:
            self.prefix = ''

        if not address:
            self.address = 'index'
            self.paired_dirname = docroot
            self.parent_dirname = docroot
        else:
            (self.paired_dirname,
             self.parent_dirname) = self._find_directories()

        self._parse_directories()
        self._read_target_file()
        self.link = self._get_link()

        if self.filename:
            self.metadata = Metadata(self.filename)

    class DocrootNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    def save(self, data):
        """Replace the contents of the file with the supplied data.

        Call the metadata object and update or create a metafile with
        the supplied data.

        Return True if everything goes according to plan.

        """

        self.filecontent = data['filecontent']

        f = open(self.filename, 'w')
        f.write(data['filecontent'])

        self.warnings.append("Saving file " + self.filename)
        self.metadata.save(data)
        return True

    def _find_directories(self):
        """Find the parent and paired directory path names.

        Return a tuple containing (paired, parent) tuples. These two
        values are the pathnames to those two directories.

        """

        paired_dirname = 'paired'
        parent_dirname = 'parent'

        split_addr = self.address.split('/')
        split_parent = split_addr
        paired = split_parent.pop()

        parent = os.path.join(self.docroot, '/'.join(split_parent))
        paired = os.path.join(parent, paired) + '/'

        return paired, parent

    def _parse_directories(self):
        """Create webnote directory structures for parent and paired dirs.

        Set global variables with Directory objects.

        Sets:

            self.parent_directory as a webnote.Directory object.
            self.paired_directory as a webnote.Directory object.

        Depends on the self.parent_dirname and self.paired_dirname
        directory pathnames having already been set.

        """

        try:
            self.parent_directory = Directory(self.parent_dirname)
        except Directory.ParseDirNotFound:
            self.warnings.append(
                'Parent directory not found: ' + self.parent_dirname)

        if self.paired_dirname == self.parent_dirname:
            self.paired_directory = self.parent_directory

        else:
            try:
                self.paired_directory = Directory(self.paired_dirname)
            except Directory.ParseDirNotFound:
                self.warnings.append(
                    'Paired directory not found: ' + self.paired_dirname)

    def _read_target_file(self):

        filename = self._find_file()

        try:
            f = open(filename, 'r')
            self.filecontent = f.read()
            self.filename = filename
        except IOError:
            self.warnings.append('Page not found: ' + self.address)

    def _find_file(self):
        """Find the page file.

        Return a string containing the filename for the page requested
        by the address. This will first try looking for the address
        with a lowercase extension in the SUFFIX['page'] list.

        If not found there, scan the page files in the parent
        directory for files with basename == address.

        """

        filename = ''
        address = ''
        if self.address:
            address = self.address

        # Check the suffixes
        for item in settings.SUFFIX['page']:
            filename = os.path.join(self.docroot, address) + item

            if os.path.isfile(filename):
                self.filename = filename
                return filename

        # Scan through the page files.
        pagename = address.split('/')[-1]

        if self.parent_directory:
            for item in self.parent_directory.get_pages():

                (basename, ext) = os.path.splitext(item)
                if (basename == pagename and
                        ext.lower() in settings.SUFFIX['page']):

                    filename = os.path.join(self.parent_dirname, item)
                    return filename

        return filename

    def _get_link(self):
        if not self.filename:
            return ('', '')

        link = os.path.join(self.prefix, self.address)
        text = os.path.basename(self.filename)
        (basename, ext) = os.path.splitext(text)
        return (link, basename)

    def _breadcrumbs(self):

        crumbs = []
        link = self.prefix
        text = self.prefix.replace('/', '')
        crumbs.append((link, text))

        steps = self.address.split('/')

        for item in steps:
            link = os.path.join(link, item)
            crumbs.append((link, item))

        return crumbs

    breadcrumbs = property(_breadcrumbs)

    def _get_title(self):
        """Compute the title as a string.

        This will be either:
        -   The title line from the metadata field.
        -   The H1 line in the content string,
        -   The filename made nice.

        At the moment, it's in "only just going" mode, and only
        returns the filename made nice.
        """

        fname = None

        if self._store_title:
            return self._store_title

        if self.filename:
            fname = os.path.basename(self.filename)

        if fname:
            basename, ext = os.path.splitext(fname)

            self._store_title = basename.replace('_', ' ')

        if self._store_title:
            return self._store_title
        else:
            return "Page title unknown"

    title = property(_get_title)

    def content(self):
        """Compute the content string.

        This will be returned as HTML code, either direct from an HTML
        page or as the product of parsing the contents of a text
        file.

        If no file is found, or it is otherwise unreadable, return an
        empty string.

        """

        if not self.filename:
            return ''

        if self._store_content:
            return self._store_content

        content = self.filecontent
        (basename, ext) = os.path.splitext(self.filename)

        source = content

        prefix = os.path.join(self.staticroot, self.address)
        figures = None

        if self.paired_directory:
            figures = self.paired_directory.get_figs()
            directory = None

        if ext in settings.SUFFIX['text']:
            if figures:
                content, unref_figs = self.reference_figures(
                    source, prefix, figures=figures)
                self._store_unref_figs = unref_figs

            content = markdown.markdown(content)

        else:
            content = self.filecontent

        self._store_content = content

        return content

    #content = property(_get_content)

    def _get_unref_figs(self):
        """List of (link, text) tuples representing unreferenced figures.

        Unreferenced figures are computed by the
        Webnote.reference_figures module, which takes a long string, a
        directory prefix and returns the modified text (which would be
        part of content) and the list of unreferenced figures.

        If calling content, the unref figs can be set global, and this
        will return that value. Likewise with the unref_figs
        attribute, which can set the content global is called first.
        """

        if self._store_unref_figs:
            return self._store_unref_figs

        # This just calls the _get_content() method, and does nothing
        # with the content value.
        content = self.content
        return self._store_unref_figs

    unref_figs = property(_get_unref_figs)

    def _get_previous(self):
        if self._store_previous:
            return self._store_previous

        link = ''
        text = ''

        previous = (link, text)

        self._store_previous = previous
        return previous

    previous = property(_get_previous)

    def _get_nextpage(self):
        if self._store_nextpage:
            return self._store_nextpage

        nextpage = []

        self._store_nextpage = nextpage
        return nextpage

    nextpage = property(_get_nextpage)

    def _get_parent(self):
        """Compute a (link, text) tuble identifying the parent

        The parent is found by this process:

        -   if it's the index, return ('/', 'index')
        -   if the page is in the docroot, return the same thing.
        -   Otherwise, return the address with the last element chopped off.
        """

        if self._store_parent:
            return self._store_parent

        link = ''
        text = ''
        prefix = ''
        if self.prefix:
            prefix = self.prefix

        if self.address == 'index':
            self._store_parent = (prefix, 'Index')
            return self._store_parent

        steps = self.address.split('/')
        if len(steps) == 1:
            self._store_parent = (self.prefix, 'Index')
            return self._store_parent

        junk = steps.pop()
        link = os.path.join(prefix, '/'.join(steps))
        text = steps[-1]

        par = (link, text)
        self._store_parent = par

        return par

    parent = property(_get_parent)

    def _get_siblings(self):
        """Return a list of (link, text) tuples identifying siblings.

        Siblings are pages in the parent directory -- that is, the
        direcotry the target page is in.
        """

        if self._store_siblings:
            return self._store_siblings

        sibs = []
        parent = self._get_parent_address()
        prefix = os.path.join(self.prefix, parent)
        sibs = self.parent_directory.link_pages(prefix)

        self._store_siblings = sibs
        return sibs

    siblings = property(_get_siblings)

    def _get_children(self):
        """Return a list of (link, text) tuples identifying children."""

        if not self.paired_directory:
            return None

        if self._store_children:
            return self._store_children

        if self.address == 'index':
            address = ''
        else:
            address = self.address

        prefix = os.path.join(self.prefix, address)
        pages = self.paired_directory.link_pages(prefix)
        kids = []
        for page in pages:
            if page[1] == 'index':
                pass
            else:
                kids.append(page)

        self._store_children = kids
        return kids

    children = property(_get_children)

    def _get_documents(self):
        """Return a list of the documents in the paired directory. """

        if not self.paired_directory:
            return None

        if self._store_documents:
            return self._store_documents

        documents = []
        if self.address == 'index':
            address = ''
        else:
            address = self.address

        prefix = os.path.join(self.prefix, address)
        documents = self.paired_directory.link_docs(prefix)
        return documents

    documents = property(_get_documents)

    def _get_parent_address(self):

        steps = self.address.split('/')

        if len(steps) > 1:
            parent = steps[:-1]
        else:
            parent = []

        parent = steps[:-1]
        parent = '/'.join(parent)

        if parent == 'index':
            parent = ''

        return parent

    def get_form_data(self):
        """Return a dictionary suitable for populating the page forms."""

        data = {
            'filecontent': self.filecontent,
            'dc_title': self.metadata.title,
            'dc_creator': self.metadata.author,
            'dc_date': self.metadata.date,
            'dc_subject': self.metadata.subject,
            'dc_description': self.metadata.description,
            'dc_contributor': self.metadata.contributor,
            'dc_coverage': self.metadata.location,
            'dc_rights': self.metadata.rights,
            'dc_source': self.metadata.source,
        }

        return data
