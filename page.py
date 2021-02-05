"""Classes interpreting the simple filesystem syntax.
"""

import os

from bs4 import BeautifulSoup
import html2text
import markdown2 as markdown
import re
import smartypants

from directory import Directory
from gallery import Gallery
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
    paired = None

    # The name and contents of the target file.
    filename = None
    filecontent = None
    unref_figs = None

    # Internal stores.
    _parent = None
    _siblings = None
    _store_content = None

    _store_files = None
    _unref_figs = None
    _store_documents = None
    _store_heading_index = None

    warnings = []

    def __init__(self, docroot, baseurl, address=None,
                 data=None, staticroot=None):
        """Create a Page object, compute parent & paired directories.

        Do the minimum necessary computations.

        - Set globals for input variables.
        - Determine if the docroot exists. Exit with exception if not.
        - Compute the addressed file & read it.
        - Compute the parent and paired directories.
        - Create a Metadata object.

        Instantiating without an address will return the index file.

        The staticroot attribute is used to override
        settings.STATIC_URL. This string is prepended to urls in the
        figures code.

        Special case: no address = docroot index.

            Instantiate without an address, and it will default to the
            docroot index.

            This looks for a file called 'index' with one of the
            values in settings.SUFFIX['page'].

        The data attribute is used to override content and metadata
        values, and can be supplied when saving an object.

        """

        if not os.path.isdir(docroot):
            raise self.DocrootNotFound(docroot)

        self.warnings = []

        self.address = address
        self.baseurl = baseurl
        self.data = data
        self.docroot = docroot

        if docroot[-1] != '/':
            self.docroot = docroot + '/'

        if address:
            (self.paired_dirname,
             self.parent_dirname) = self._find_directories()
            if address[-1] == '/':
                self.address = address[:-1]

        else:
            self.paired_dirname = docroot
            self.parent_dirname = docroot

        if staticroot:
            self.staticroot = staticroot
        else:
            self.staticroot = settings.STATIC_URL

        (self.parent_directory,
         self.paired) = self._parse_directories()

        self.filename = self._find_filename(docroot, address)
        self.filecontent = self._read_target_file(self.filename)

        self.link = self._get_link()

        self.metadata = Metadata(self.filename, data)
        self.parent = self._find_parent()

        if len(self.metadata.pagetype()) > 0:
            if self.metadata.pagetype()[0] == 'gallery':

                try:
                    self.gallery = Gallery(
                        docroot=docroot, baseurl=baseurl, address=address,
                    )
                except Gallery.DirectoryNotFound:
                    self.gallery = None

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

    def _find_filename(self, docroot, address):
        """Find the page file, return a filename.

        Return a string containing the filename for the page requested
        by the address. This will first try looking for the address
        with a lowercase extension in the SUFFIX['page'] list.

        If no file is found, try "index".[page suffix].

        If not found there, scan all the page files in the parent
        directory for files with basename == address.

        """

        filename = ''

        if not address:
            address = ''
#       Check the suffixes
        for item in settings.SUFFIX['page']:
            filename = os.path.join(docroot, address) + item

            if os.path.isfile(filename):
                self.filename = filename
                return filename

#       Scan through the page files.
        if self.parent_directory:
            for item in self.parent_directory.model['page']:
                (basename, ext) = os.path.splitext(item)
                if basename == 'index':
                    filename = os.path.join(docroot, address) + item
                    return filename

#       It's not a file. Return a standard filename.
        if address:
            filename = os.path.join(docroot, address + '.md')
        else:
            filename = None
        return filename

    def _find_parent(self):
        """Return a Page object representing the parent."""

        address = self.address

        if not self.address:
            return None

        address, fname = os.path.split(self.address)
        return Page(self.docroot, self.baseurl, address)

    def _parse_directories(self):
        """Create webnote directory structures for parent and paired dirs.

        Return parent and paired directory objects.

        Sets:

            self.parent_directory as a webnote.Directory object.
            self.paired as a webnote.Directory object.

        Depends on the self.parent_dirname and self.paired_dirname
        directory pathnames having already been set.

        """

        parent = None
        paired = None

        try:
            parent = Directory(
                dirpath=self.parent_dirname,
                docroot=self.docroot,
                baseurl=self.baseurl,
            )
        except Directory.ParseDirNotFound:
            self.warnings.append(
                'Parent directory not found: ' + self.parent_dirname)

        if self.paired_dirname == self.parent_dirname:
            paired = parent

        else:
            try:
                paired = Directory(
                    dirpath=self.paired_dirname,
                    docroot=self.docroot,
                    baseurl=self.baseurl,
                )
            except Directory.ParseDirNotFound:
                self.warnings.append(
                    'No paired directory.')

        return(parent, paired)

    def _read_target_file(self, filename):

        filecontent = ''

        if not filename:
            return None

        try:
            f = open(filename, 'r')
            filecontent = f.read()
        except IOError:
            if self.address:
                self.warnings.append('Page not found: ' + self.address)
            else:
                self.warnings.append('Index page not found.')
            return None

        return filecontent

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
                crumbs.append((link, item.replace('_', ' ')))

        crumbs.append((self.previous()[0], 'prev'))
        crumbs.append((self.nextpage()[0], 'next'))

        return crumbs

    def children(self):
        """Return a list of page objects comprising this page's children.
        """

        if not self.paired:
            return None

        address = ''
        if self.address:
            address = self.address

        filename = ''
        if self.filename:
            filename = self.filename

        (path, fname) = os.path.split(filename)

        children = []

        child_pages = self.paired.model['page']
#       Handle the sort reverse command.
        if len(self.metadata.metadata['sort']):
            if self.metadata.metadata['sort'][0] == 'reverse':
                child_pages = sorted(child_pages, reverse=True)

        for page in child_pages:
            (basename, ext) = os.path.splitext(page)
            if basename.lower() == 'index':
                pass
            else:
                addr = os.path.join(address, basename)
                p = Page(self.docroot, self.baseurl, addr)
                children.append(p)

        return children

    def child_links(self, baseurl=None):
        """Return a list of (link, text) tuples identifying children."""

        if not self.paired:
            return None

        if self.address:
            address = self.address
        else:
            address = ''

        if not baseurl:
            baseurl = os.path.join(self.baseurl, address)

        pages = self.paired.pages(baseurl)

        kids = []
        for page in pages:
            if page[1] == 'index':
                pass
            else:
                kids.append(page)

#       Handle the sort reverse command.
        if len(self.metadata.metadata['sort']):
            if self.metadata.metadata['sort'][0] == 'reverse':
                kids = sorted(kids, reverse=True)

        return kids

    def concordance(self):
        """List words and word counts, in a table."""

        concordance = {}

        h = html2text.HTML2Text()
        h.ignore_links = True
        source = h.handle(self.content().decode('utf8'))

        words = source.split()

        for word in words:
            word = word.lower()
            word = word.replace('_', '')
            word = word.replace('(', '')
            word = word.replace(')', '')
            word = word.replace('#', '')
            word = word.replace('.', '')
            word = word.replace(',', '')
            word = word.replace('?', '')
            word = word.replace('"', '')
            word = word.replace('--', '')
            word = word.replace('*', '')
            word = word.replace('!', '')

            if len(word) > 0:
                
                if word[0] == "'":
                    word = word[1:]

                if word[-1] == "'":
                    word = word[:-1]

                if word[0] == "`":
                    word = word[1:]

                if word[-1] == "`":
                    word = word[:-1]

                if word not in concordance.keys():
                    concordance[word] = 1
                else:
                    concordance[word] += 1

        # Cnvert the dictionary into a sorted list.
        data = []
        for item in sorted(concordance.keys()):
            data.append((item, concordance[item]))
                    
        return data

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
        if not content:
            content = ''

        (basename, ext) = os.path.splitext(self.filename)

        source = content

        baseurl = self.baseurl
        if baseurl[0] == '/':
            baseurl = self.baseurl[1:]

        baseurl = os.path.join(self.staticroot, baseurl)
        if self.address:
            baseurl = os.path.join(self.staticroot, baseurl, self.address)

        figures = None

        if self.paired:
            figures = self.paired.model['figures']
            directory = None

        if ext in settings.SUFFIX['html']:
            content = self.filecontent
        else:
            if figures:
                (content, unref_figs) = self.reference_figures(
                    source, baseurl, figures=figures
                )
                self._unref_figs = unref_figs
            else:
                content = self.filecontent

            if content:
                content = markdown.markdown(content)

        # Find the H1 line in the content string
        soup = BeautifulSoup(content, "html.parser")
        h1 = soup.find_all('h1')
        # If it's not there, insert one created from the filename.
        if not len(h1):
            h1 = "<h1 class='noprint'>"
            h1 += self.title_from_fname().replace('_', ' ')
            h1 += "</h1>\n\n"
            content = h1 + content

        # Compile a headings index.
        heading_index = None
        headings = soup.find_all(['h2', 'h3', 'h4'])
        if len(headings) > 0:
            heading_index = []
            count2 = 0
            count3 = 0
            count4 = 0

            for h in headings:
                if h.name == 'h2':
                    count2 +=1
                    link = h.name + '-' + str(count2)
                elif h.name == 'h3':
                    count3 +=1
                    link = h.name + '-' + str(count3)
                elif h.name == 'h4':
                    count4 +=1
                    link = h.name + '-' + str(count4)

                for f in h.descendants:
                    text = f

                heading_index.append((link, text))
                h['id'] = link

            self._store_heading_index = heading_index

        content = str(soup)

        content = self.replacements(content)

        self._store_content = content

        return self._store_content

    def content_novel(self):
        """Stitch all the siblings together into a single document.

        Move all the headings one level down, so H1 becomes H2 and so on.

        """

        content = ""

        for child in self.children:
            content += "\n\n<!-- ------------------- -->\n" + child.content

        return content

    def documents(self):
        """Return a list of the documents in the paired directory. """

        if not self.paired:
            return None

        if self._store_documents:
            return self._store_documents

        documents = []
        if not self.address:
            address = ''
        else:
            address = self.address

        baseurl = os.path.join(self.baseurl, address)
        documents = self.paired.link_docs(baseurl)
        return documents

    def formdata(self):
        """Return a dictionary suitable for populating the page forms."""

        data = self.metadata.formdata()
        data['content'] = self.filecontent
        return data

    def heading_index(self):
        if self._store_heading_index:
            return self._store_heading_index

        self.content()
        return self._store_heading_index

    def nextpage(self):

        address = ''
        if self.address:
            address = self.address
        filename = ''
        if self.filename:
            filename = self.filename

        link = ''
        n = 0
        siblings = self.parent_directory.model['page']
        text = "The previous page has no name"

        (path, fname) = os.path.split(filename)
        if fname in siblings:
            n = siblings.index(fname)

        path, basename = os.path.split(address)

        if n == len(siblings)-1:
            link = None
            text = None

        else:
            try:
                (basename, ext) = os.path.splitext(siblings[n+1])
                link = os.path.join(self.baseurl, path, basename)
                text = basename
            except IndexError:
                link = None
                text = None

        nextpage = (link, text)

        return nextpage

    def parent_link(self):
        """Compute a (link, text) tuble identifying the parent

        The parent is found by this process:

        -   if it's the index, return ('/', 'index')
        -   if the page is in the docroot, return the same thing.
        -   Otherwise, return the address with the last element chopped off.
        """

        link = ''
        text = ''
        baseurl = ''

        if self.baseurl:
            baseurl = self.baseurl

        if not self.address:
            return (baseurl, 'Index')

        steps = self.address.split('/')
        if len(steps) == 1:
            return (self.baseurl, 'Index')

        junk = steps.pop()
        link = os.path.join(baseurl, '/'.join(steps))
        text = steps[-1]

        return (link, text)

    def previous(self):

        address = ''
        if self.address:
            address = self.address

        filename = ''
        if self.filename:
            filename = self.filename

        link = ''
        n = 0
        siblings = self.parent_directory.model['page']
        text = "The previous page has no name"

        (path, fname) = os.path.split(filename)
        if fname in siblings:
            n = siblings.index(fname)

        path, basename = os.path.split(address)

        if n == 0:
            link = None
            text = None

        else:
            (basename, ext) = os.path.splitext(siblings[n-1])
            link = os.path.join(self.baseurl, path, basename)
            text = basename

        previous = (link, text)

        return previous

    def replacements(self, content):
        """Replace quote characters and the like.
        """

        return smartypants.smartypants(content)

    def save(self, data, files=None):
        """Replace the contents of the file with the supplied data.

        Call the metadata object and update or create a metafile with
        the supplied data.

        The attribute data is a dictionary:

            'content': 'string containing contents to be written to file',
            'dc_title': dc_title,
            ...

        Return True if everything goes according to plan.

        """

        address = self.address
        if address == 'index':
            address = ''

        filename = self.filename

        if 'newfilename' in data.keys():
            fname = data['newfilename'].replace(' ', '_')
            filename = os.path.join(
                self.parent_directory.dirpath, fname + '.md')
        else:
            filename = self.filename

        if 'content' in data.keys():
            filecontent = data['content']
            f = open(filename, 'w')
            f.write(filecontent)
            self.filename = filename

        if not self.paired:
            path = os.path.join(self.docroot, self.address)
            os.mkdir(path)

        if files:
            f = files['filename']
            filepath = os.path.join(
                self.docroot, self.address, str(files['filename']))

            with open(filepath, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)

        self.metadata.save(data)

        return True

    def siblings(self):
        """Return a list of page objects comprising this page's siblings.
        """

        # If this is the index, it has no siblings, only children.
        if not self.address:
            return None

        # If we have been this way before...
        if self._siblings:
            return self._siblings

        siblings = []
        steps = self.address.split('/')

        pages = self.parent_directory.model['page']

        if self.parent.metadata.metadata['sort']:
            if self.parent.metadata.metadata['sort'][0] == 'reverse':
                pages = sorted(pages, reverse=True)

        for page in pages:
            (basename, ext) = os.path.splitext(page)
            path = '/'.join(steps[:-1])
            address = os.path.join(path, basename)

            if basename == steps[-1]:
                pass
            else:
                sib = Page(self.docroot, self.baseurl, address)
                siblings.append(sib)

        # Store the result, so we don't have to compute it again.
        self._siblings = siblings
        return siblings

    def sibling_links(self, baseurl=None):
        """Return a list of (link, text) tuples identifying siblings.

        Siblings are pages in the parent directory -- that is, the
        directory the target page is in.
        """

        address = ''
        basename = ''
        filename = ''
        path = ''
        sibs = []

        if self.address:
            address = self.address
        (path, basename) = os.path.split(address)

        baselink = os.path.join(self.baseurl, path)

        if self.filename:
            filename = self.filename

        (path, fname) = os.path.split(filename)

        pages = self.parent_directory.model['page']

        if self.parent.metadata.metadata['sort']:
            pages = sorted(pages, reverse=True)

        for page in pages:
            (basename, ext) = os.path.splitext(page)

            if basename.lower() == 'index':
                pass
            else:

                if page == fname:
                    link = None
                else:
                    link = os.path.join(baselink, basename)

                sibs.append((link, basename.replace('_', ' ')))

        return sibs

    def thumbnail(self):
        """Return a (src, alt) tuple for the page'sthumbnail file."""

        if self.paired:
            for item in self.paired.model['figures']:
                (basename, ext) = os.path.splitext(item)
                if basename.lower() == 'thumbnail':
                    src = os.path.join(
                        self.staticroot + self.baseurl, self.address, item)
                    alt = item
                    return (src, item)

        return False

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

#       Find the H1 line in the content string.
#        soup = BeautifulSoup(self.content(), "html.parser")
#        h1 = soup.find_all('h1')
#        for element in h1:
#            return element.string

#       No h1 tag? Prettify the filename.
        if self.filename:
            fname = os.path.basename(self.filename)
            basename, ext = os.path.splitext(fname)
            return basename.replace('_', ' ')

        return "Title unknown"

    def title_from_fname(self):

        title = ''
        if self.filename:
            fname = os.path.basename(self.filename)
            (basename, ext) = os.path.splitext(fname)
            title = basename.replace(' ', '_')

        return title

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

        if self._unref_figs:
            return self._unref_figs

        # This just calls the _get_content() method, and does nothing
        # with the content value.
        content = self.content()
        return self._unref_figs

    def wordcount(self):
        """Return the number of words in a text file."""

        if not self.filecontent:
            return 0

        return len(self.filecontent.split())
