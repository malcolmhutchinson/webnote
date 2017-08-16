"""Classes interpreting the simple filesystem syntax.
"""

import os

from bs4 import BeautifulSoup
import markdown2 as markdown

from directory import Directory
from metadata import Metadata
import settings
from webnote import Webnote


class Page(Webnote):
    """Compute data about a page within a simple syntax filesystem.

    This class computes data surrounding a page object, giving it
    context. It finds the parent, siblings, previous and next pages,
    the marked-up content of the text file, and a list of child pages
    if any exist.

    A page is a text or HTML file within the document root
    filesystem. It may have a directory with the same basename
    associated with it (the pared directory), which is where any child
    pages, and any images referred to in the text, will be found. It
    may also have a metadata file associated with it.


    ### Usage

        webnote.page.Page(docroot, baseurl, address)

    Initialise with a docroot string, pointing to the root directory
    for an archive. If no address is supplied, it will look for a page
    called 'index'.

    Docroot and baseurl map file path to url. The address is appended
    to each to provide a full path or url.

    Provides the following methods:

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


    Optional arguments

    To save a Page object, include a dictionary containing string
    values for fields in settings.DC_METADATA.

        webnote.page.Page(docroot, baseurl, address, data=data)

    """

    docroot = None
    address = None
    baseurl = None
    metadata = None

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
    _store_content = None
    _store_parent = None
    _store_files = None
    _store_unref_figs = None
    _store_documents = None

    warnings = []

    def __init__(self, docroot, baseurl, address=None,
                 data=None, staticroot=None
    ):
        """Instantiating without an address will return the index file.

        Do the minimum necessary computations.

        - Set globals for input variables.
        - Determine the docroot exists. Exit with exception if not.
        - Compute the addressed file & read it. Exit with exception
          if this file is not found.
        - Compute the parent and paired directories.
        - Create a Metadata object.

        The staticroot attirbute is used to override
        settings.STATIC_URL. This string is prepended to urls in the
        figures code.

        Special case: no address = docroot index.

            Instantiate without an address, and it will default to the
            docroot index.

            This looks for a file called 'index' with one of the
            values in settings.SUFFIX['page']. If it doesn't find one,
            it addeds a line to the warnings list.

        """

        if not docroot:
            raise self.DocrootNotFound(docroot)

        if not os.path.isdir(docroot):
            raise self.DocrootNotFound(docroot)

        self.warnings = []

        self.docroot = docroot
        if docroot[-1] != '/':
            self.docroot = docroot + '/'

        self.address = address

        if address:
            (self.paired_dirname,
             self.parent_dirname) = self._find_directories()
            if address[-1] == '/':
                self.address = address[:-1]

        else:
            self.paired_dirname = docroot
            self.parent_dirname = docroot

        if baseurl:
            self.baseurl = baseurl
        else:
            self.baseurl = '/'

        if staticroot:
            self.staticroot = staticroot
        else:
            self.staticroot = settings.STATIC_URL
            
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

    class DocumentNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)


    def get_absolute_url(self):
        if self.address:
            return os.path.join(self.baseurl, self.address)

        return self.baseurl
        
    url = property(get_absolute_url)
    
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

    def _find_file(self):
        """Find the page file, return a filename.

        Return a string containing the filename for the page requested
        by the address. This will first try looking for the address
        with a lowercase extension in the SUFFIX['page'] list.

        If no file is found, try "index".[page suffix].

        If not found there, scan all the page files in the parent
        directory for files with basename == address.

        """

        filename = ''
        address = ''
        if self.address:
            address = self.address

#       Check the suffixes
        for item in settings.SUFFIX['page']:
            filename = os.path.join(self.docroot, address) + item

            if os.path.isfile(filename):
                self.filename = filename
                return filename

#       Scan through the page files.
        if self.parent_directory:
            for item in self.parent_directory.model['page']:
                (basename, ext) = os.path.splitext(item)
                if basename =='index':
                    filename = os.path.join(self.docroot, address) + item
                    return filename
        
        return filename

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
                    'No paired directory.')
            
    def _read_target_file(self):

        filename = self._find_file()

        try:
            f = open(filename, 'r')
            self.filecontent = f.read()
            self.filename = filename
        except IOError:
            if self.address:
                self.warnings.append('Page not found: ' + self.address)
            else:
                self.warnings.append('Index page not found.')
            return False

        return True

    def _get_link(self):
        if not self.filename:
            return ('', '')

        link = self.baseurl
        if self.address:
            link = os.path.join(self.baseurl, self.address)
        text = os.path.basename(self.filename)
        (basename, ext) = os.path.splitext(text)
        return (link, basename)

    def _get_parent_address(self):

        if self.address:

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

        return ''

    def breadcrumbs(self):
        """A list of (link, text) tuples climbing back up the hierachy.

        Start with the baseurl, then explode the address by slashes."""
        
        link = self.baseurl
        text = self.baseurl
        crumbs = [(link, text)]

        if self.address:
            steps = self.address.split('/')
            for item in steps:
                link = os.path.join(link, item)
                crumbs.append((link, item))

        crumbs.append((self.previous()[0], 'prev'))
        crumbs.append((self.nextpage()[0], 'next'))

        return crumbs

    def children(self, baseurl=None):
        """Return a list of (link, text) tuples identifying children."""

        if not self.paired_directory:
            return None

        if self.address:
            address = self.address
        else:
            address = ''

        if not baseurl:
            baseurl = os.path.join(self.baseurl, address)

        pages = self.paired_directory.pages(baseurl)

        kids = []
        for page in pages:
            if page[1] == 'index':
                pass
            else:
                kids.append(page)

        return kids

    def content(self):
        """Compute the content string.

        This will be returned as HTML code, either direct from an HTML
        page or as the product of parsing the contents of a text
        file.

        If no file is found, or it is otherwise unreadable, return an
        empty string. 

        Computing the content necessarily computes unreferenced
        figures, and vice-versa. To prevent duplication, the results
        of the computation are stored, in store_content, and
        store_unref_figs, respectively. 

        """

        if not self.filename:
            if not self.address:
                return "<h1>Index " + self.baseurl + "</h1>"
            return "<h1>No file found " + self.address + "</h1>"
        
        if self._store_content:
            return self._store_content

        content = self.filecontent

        (basename, ext) = os.path.splitext(self.filename)

        source = content

        baseurl = self.baseurl
        if baseurl[0] == '/':
            baseurl = self.baseurl[1:]

            
        baseurl = os.path.join(self.staticroot, baseurl)
        if self.address:
            baseurl = os.path.join(self.staticroot, baseurl, self.address)

        figures = None

        if self.paired_directory:
            figures = self.paired_directory.get_figs()
            directory = None
        if ext in settings.SUFFIX['text']:
            if figures:
                content, unref_figs = self.reference_figures(
                    source, baseurl, figures=figures)
                self._store_unref_figs = unref_figs

            content = markdown.markdown(content)
        else:
            content = self.filecontent

        self._store_content = content

        return content

    def documents(self):
        """Return a list of the documents in the paired directory. """

        if not self.paired_directory:
            return None

        if self._store_documents:
            return self._store_documents

        documents = []
        if not self.address:
            address = ''
        else:
            address = self.address

        baseurl = os.path.join(self.baseurl, address)
        documents = self.paired_directory.link_docs(baseurl)
        return documents

    def form_data(self):
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

    def nextpage(self):

        link = ''
        text = "the next pages isn't named yet"

        nextpage = (link, text)


        return nextpage

    def parent(self):
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
        baseurl = ''
        if self.baseurl:
            baseurl = self.baseurl

        if not self.address:
            self._store_parent = (baseurl, 'Index')
            return self._store_parent

        steps = self.address.split('/')
        if len(steps) == 1:
            self._store_parent = (self.baseurl, 'Index')
            return self._store_parent

        junk = steps.pop()
        link = os.path.join(baseurl, '/'.join(steps))
        text = steps[-1]

        par = (link, text)
        self._store_parent = par

        return par

    def previous(self):

        link = ''
        text = "The previous page has no name"

        previous = (link, text)

        return previous

    def save(self, data):
        """Replace the contents of the file with the supplied data.

        Call the metadata object and update or create a metafile with
        the supplied data.

        The attribute data is a dictionary:

        {
            'filecontent': string,
            'metadata': metadata object,
        }

        Return True if everything goes according to plan.

        """

        if 'content' in data.keys():
        
            filecontent = data['content']
            f = open(self.filename, 'w')
            f.write(filecontent)

        self.metadata.save(data)

        return True

    def siblings(self, baseurl=None):
        """Return a list of (link, text) tuples identifying siblings.

        Siblings are pages in the parent directory -- that is, the
        direcotry the target page is in.
        """

        sibs = []
        parent = self._get_parent_address()
        if not baseurl:
            baseurl = os.path.join(self.baseurl, parent)

        sibs = self.parent_directory.pages(baseurl)

        return sibs

    def title(self):
        """Compute the title as a string.

        This will be either:
        -   The title line from the metadata field.
        -   The H1 line in the content string,
        -   The filename made nice.

        If there is more than one h1 line in the file, it will take
        the first one it finds.

        """

        title = None

#       Search the metarecord first.
        if self.metadata:
            if self.metadata.title():
                return self.metadata.title()

#       Find the H1 line in the content string        
        soup = BeautifulSoup(self.content(), "html.parser")
        h1 = soup.find_all('h1')
        for element in h1:
            return element.string

#       No h1 tag? Prettify the filename.
        if self.filename:
            fname = os.path.basename(self.filename)
            basename, ext = os.path.splitext(fname)
            return basename.replace('_', ' ')

        return "Title unknown"


    def unref_figs(self):
        """List of (link, text) tuples representing unreferenced figures.

        Unreferenced figures are computed by the
        Webnote.reference_figures module, which takes a long string, a
        url baseurl and returns the modified text (which would be part
        of content) and the list of unreferenced figures.

        If calling content, the unref figs can be set global, and this
        will return that value. Likewise with the unref_figs
        attribute, which can set the content global is called first.

        """

        if self._store_unref_figs:
            return self._store_unref_figs

        # This just calls the _get_content() method, and does nothing
        # with the content value.
        content = self.content()
        return self._store_unref_figs





