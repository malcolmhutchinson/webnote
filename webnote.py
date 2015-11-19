"""Webnote. Classes to implement the simple filesystem syntax.

"""

import csv
import os
import settings
import re
import cgi
from markdown2 import markdown

class Webnote():
    """Base class for the webnote application. 

    This class implements standard methods, like the parsing of a
    directory into file types.
    """

    warnings = []

    def parse_directory(self, directory):
        """Return a dictionary containing lists of files by type.

        It looks for keys in the settings.SUFFIX variable. The output
        dictionary will have elemements corresponding to the keys of
        this dictionary. It will also contain elements "dirs",
        "hidden" and "all".

        Hidden files start with a period. Temporary files end with a
        tilde.
        """

        if settings.DEBUG:
            print "--> webnote.Webnote.parse_directory"

        if not os.path.isdir(directory):
            raise self.ParseDirNotFound(directory)

        output = {
            'dirs': [],
            'hidden': [],
            'temp': [],
        }

        for key in settings.SUFFIX:
            output[key] = []

        listing = sorted(os.listdir(directory))

        for item in listing:
            if item[0] == '.':
                output['hidden'].append(item)

            elif item[-1] == '~':
                output['temp'].append(item)

            elif os.path.isdir(os.path.join(directory, item)):
                output['dirs'].append(item)

            else:
                basename, ext = os.path.splitext(item)

                for key in settings.SUFFIX:
                    if ext.lower() in settings.SUFFIX[key]:
                        output[key].append(item)

        output['all'] = listing

        return output

    class ParseDirNotFound(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

    def reference_figures(self, source, directory, prefix, figures=None):
        """Convert coded references to figures in a text into HTML.

        Given a source text containing references to image files in
        the simple syntax format of:

            [[image.jpg Anything following the first space is a caption.]]
 
        And the name of a dirtectory in which to find the image files,
        return a copy of the text with figure/caption references
        converted to valid html, and a list of unreferenced figures.

        The prefix is appended to the <img src> attribute to complete
        the link.

        Optionally, the figures can be supplied as a list of filenames
        -- as found in the webnote parsed directory
        structure['figures'] structure. Supplying this lise will
        suppress calling the parse_directory method.

        """

        if settings.DEBUG:
            print "--> webnote.Webnote.reference_figures"

        output = source
        unref = []
        links = []

        expression = r'\[\[.*\]\]'
        p = re.compile(expression)
        result = p.findall(source)

        if not figures:
            d = self.parse_directory(directory)
            figures = d['figure']

        for figure in figures:
            link = os.path.join(prefix,figure)
            caption = figure
            unref.append((link, caption))

        for match in result:
            (link, html) = self._figure_html(match, prefix)
            output = output.replace(match, html)

            links.append(link)

            for fig in unref:
                if fig[1] == link[0]:
                    unref.pop(unref.index(fig))

        return output, unref

    def _figure_html(self, match, prefix):
        """Replace a match code with the HTML DIV for displaying an image.

        - Strip off the square brackets at each end.
        - Break the remaining string by whitespace. The first of these
          will be the filename.
        - Put the remaining string back together.
        - Construct the HTML output string.
        """

        if settings.DEBUG:
            print "--> webnote.Webnote._figure_html"

        content = match.replace('[[', '')
        content = content.replace(']]', '')
        content = content.strip()

        words = content.split(' ')
        filename = words.pop(0)

        if prefix:
            filepath = os.path.join(prefix, filename)
        else:
            filepath = filename

        caption = ''

        for word in words:
            caption += word + ' '

        caption = caption.strip()
        caption = cgi.escape(caption)

        link = (filename, caption)
        caption = caption.replace("'", "&#39;")

        html = ''
        html += "<div class='figure'>\n"
        html += "    <img src='" + filepath + "' "
        html += "alt='" + filename + "' />\n"
        html += "    <p class='caption'>" + caption
        html += "</p>\n"
        html += '</div>\n\n'

        return (link, html)


class Page(Webnote):
    """Compute metadata about a page within a simple syntax filesystem. 

    This class computes data surrounding a page object, giving it
    context. It finds the parent, previous and next pages, the
    marked-up content of the text file, and a list of child pages if
    any exist.

    A page is a text or HTML file within the document root
    filesystem. It may have a directory with the same basename
    associated with it (the pared directory), which is where any child
    pages, and any images referred to in the text, will be found. . It
    may also have a metadata file associated with it.

    Provides the following attributes:

        title      A computed title for the page.
        content    Marked-up text content of the file.
        parent     Link tuple to the parent page.
        previous   Link tuple to the Previous page in a series.
        nextpage   Link tuple to the Next page in a series.
        siblings   List of link tuples to other pages in the same directory.
        children   List of link tuples to pages in the paired directory.

    A link tuple has the form (link, text), and is intended to go into
    a Django template like this:

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
    _store_docs = None
    _store_img_hires = None

    warnings = []

    def __init__(self, docroot, address=None, prefix=None):
        """Instantiating without an address will return the index file.

        Do the minimum necessary computations. 
        - Set globals for input variables.
        - Determine the docroot exists. Exit with exception if not.
        - Compute the addressed file & read it.
        - Compute the parent and paired directories.

        Special case: no address = docroot index.

            Instantiate without an address, and it will default to the
            docroot index.

            This looks for a file called 'index' with one of the
            values in settings.SUFFIX['page']. If it doesn't find one,
            it addeds a line to the warnings list.

        """

        if settings.DEBUG:
            print "--> webnote.Page.init"
        
        if not os.path.isdir(docroot):
            raise self.DocrootNotFound(docroot)

        self.warnings = []

        self.docroot = docroot
        if docroot[-1] != '/':
            self.docroot = docroot + '/'

        self.address = address
        if address[-1] == '/':
            self.address = address[:-1]

        self.prefix = prefix

        if not address:
            self.address = 'index'
            self.paired_dirname = docroot
            self.parent_dirname = docroot
        else:
            (self.paired_dirname, self.parent_dirname) = self._find_directories()

        self._parse_directories()
        self._read_target_file()

    class DocrootNotFound(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

    def _find_directories(self):
        """Find the parent and paired directories.

        """
        if settings.DEBUG:
            print "--> webnote.Page._find_directories"

        paired_dirname = 'paired'
        parent_dirname = 'parent'

        split_addr = self.address.split('/')
        split_parent = split_addr
        paired = split_parent.pop()

        parent = self.docroot + '/'.join(split_parent) +'/'
        paired = os.path.join(parent, paired) +'/'

        return paired, parent

    def _parse_directories(self):

        if settings.DEBUG:
            print "--> webnote.Page._parse_directories"
            
        try:
            self.parent_directory = self.parse_directory(self.parent_dirname)
        except self.ParseDirNotFound:
            self.warnings.append(
                'Parent directory not found: ' +
                self.parent_dirname)
            
        if self.paired_dirname == self.parent_dirname:
            self.paired_directory = self.parent_directory

        else:
            try:
                self.paired_directory = self.parse_directory(self.paired_dirname)
            except self.ParseDirNotFound:
                self.warnings.append(
                    'Paired directory not found: ' + self.paired_dirname)
 
    def _read_target_file(self):

        if settings.DEBUG:
            print "--> webnote.Page._read_target_file"

        filename = self._find_file()
        
        try:
            f = open(filename, 'r')
            self.filecontent = f.read()
            self.filename = filename
        except IOError:
            self.warnings.append('Page not found: ' + self.address)

        if settings.DEBUG:
            if self.warnings:
                idx = 1
                print "WARNINGS"
                for warning in self.warnings:
                    print idx, warning
                    idx +1

    def _find_file(self):
        """Find the page file.

        Return a string containing the filename for the page requested
        by the address. This will first try looking for the address
        with a lowercase extension in the SUFFIX['page'] list. 

        If not found there, scan the page files in the parent
        directory for files with basename == address

        """

        if settings.DEBUG:
            print "--> webnote.Page._find_file"

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
            for item in self.parent_directory['page']:
                
                (basename, ext) = os.path.splitext(item)
                    
                if (basename == pagename and
                    ext.lower() in settings.SUFFIX['page']):

                    filename = os.path.join(self.parent_dirname, item)
                    return filename

        return filename

    def _get_title(self):
        """Compute the title as a string.

        This will be either:
        -   The title line from the metadata field.
        -   The H1 line in the content string,
        -   The filename made nice.
        """

        if self._store_title:
            return self._store_title

        if settings.DEBUG:
             print "--> webnote.Page._get_title"   
        
        fname = os.path.basename(self.filename)
        basename, ext = os.path.splitext(fname)
        self._store_title = basename.replace('_', ' ')

        return self._store_title

    title = property(_get_title)    
    
    def _get_content(self):
        """Compute the content string.

        This will be returned a HTML code, either direct from an HTML
        page or as the product of parsing the contents of a text
        file.

        """
        if self._store_content:
            return self._store_content

        if settings.DEBUG:
             print "--> webnote.Page._get_content"   

        content = ''

        if self.filecontent:
            content = self.filecontent
        
        self._store_content = content
        return content

    content = property(_get_content)

    def _get_unref_figs(self):
        """List of (link, text) tuples representing unreferenced figures.
        """
        
        if self.store_unref_figs:
            return self.store_unref_figs
        
        unref_figs = []
        if settings.DEBUG:
             print "--> webnote.Page._get_unref_figs"   

        self._store_unref_figs = unref_figs
        return unref_figs

    unref_figs = property(_get_unref_figs)
    
    def _get_previous(self):
        if self._store_previous:
            return self._store_previous

        if settings.DEBUG:
             print "--> webnote.Page._get_previous"   

        link = ''
        text =''
        
        previous = (link, text)

        self._store_previous = previous
        return previous
    
    previous = property(_get_previous)

    def _get_nextpage(self):
        if self._store_nextpage:
            return self._store_nextpage

        if settings.DEBUG:
             print "--> webnote.Page._get_nextpage"   
        
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
        
        if settings.DEBUG:
            print "--> webnote.Page._get_parent"

        link = 'link'
        text = 'text'

        if self.address == 'index':
            self._store_parent = self.prefix + '/', 'Index'
            return self.prefix + '/', 'Index'

        steps = self.address.split('/')

        if len(steps) == 1:
            self._store_parent = self.prefix + '/', 'Index'
            return self.prefix + '/', 'Index'
        
        junk = steps.pop()
        link = self.prefix + "/" + '/'.join(steps) + '/'
        text = steps[-1]
        
        parent = (link, text)
        self._store_parent = parent
        return parent

    parent = property(_get_parent)
    
    def _get_siblings(self):
        """Return a list of (link, text) tuples identifying siblings.

        Siblings are pages in the parent directory -- that is, the
        direcotry the target page is in.
        """
        
        if self._store_siblings:
            return self._store_siblings

        if settings.DEBUG:
             print "--> webnote.Page._get_siblings"   
        
        siblings = []
        parent = self._get_parent_address()

        for item in self.parent_directory['page']:
            (basename, ext) = os.path.splitext(item)
            link = self.prefix + '/' + parent +'/' + basename + '/'
            text = basename
            siblings.append((link, text))
        
        self._store_siblings = siblings
        return siblings

    siblings = property(_get_siblings)
        
    def _get_children(self):
        """Return a list of (link, text) tuples identifying siblings."""

        if not self.paired_directory:
            return None

        if self._store_children:
            return self._store_children

        if settings.DEBUG:
             print "--> webnote.Page._get_children"   
        
        children  = []
        parent = self._get_parent_address()

        for item in self.paired_directory['page']:
            (basename, ext) = os.path.splitext(item)
            link = self.prefix + '/' + parent +'/' + basename + '/'
            text = basename
            children.append((link, text))

        self._store_children = children
        return children
    
    children = property(_get_children)

    def _get_docs(self):
        """Return a list of (link, text) tuples identifying document files."""

        if self._store_docs:
            return self._store_docs

        if settings.DEBUG:
             print "--> webnote.Page._get_docs"   
        
        docs = []
        parent = self._get_parent_address()

        for item in self.parent_directory['docs']:
            print item
            (basename, ext) = os.path.splitext(item)
            link = self.prefix + '/' + parent +'/' + basename + '/'
            text = basename
            docs.append((link, text))

        self._store_docs = docs
        return docs
    
    docs = property(_get_docs)

    def _get_img(self):
        """Return a list of (link, text) tuples identifying image files."""

        if self._store_img_hires:
            return self._store_img_hires

        if settings.DEBUG:
             print "--> webnote.Page._get_img"   
        
        img_hires = []

        self._store_img_hires = img_hires
        return img_hires

    img_hires = property(_get_img)

    def _get_parent_address(self):
        steps = self.address.split('/')
        parent = steps[:-1]
        parent = '/'.join(parent)
        return parent
                

class Metadata():
    """Provide services for dealing with metadata.

    This class knows all about the metadata files. Give it an address,
    and it will determine where the file is, read it and return a
    dictionary of key/value pairs.

    It can also write a metadata file, given a list containing lines
    to be written into the file. Each item in the list is a (key,
    value) tuple.

    A Dublin Core metadata record looks like this:

        # Dublin Core metadata
        DC.Title:       Webnote
        DC.Creator:     Malcolm Hutchinson
        DC.Subject:     Filesystem syntax, information systems, Django, Python
        DC.Description: Filesystem services implimenting the simple syntax.
        DC.Contributor: 
        DC.Coverage:    New Zealand
        DC.Date:        2015-04-03
        DC.Type:        
        DC.Format:      text/html
        DC.Source:      
        DC.Language:    en
        DC.Identifier:
        DC.Publisher:   archaeography.co.nz
        DC.Publisher:   Malcolm Hutchinson
        DC.Relation:    
        DC.Rights:      cc-by
        # END DC metadata

    This class takes a page address, which is the address generated by
    a Webnote object, pointing to a page (text or HTML file).
    """
    
    address = None
    fileLines = []

    dc_metadata = {
        "DC.Title": [],
        "DC.Creator": [],
        "DC.Subject": [],
        "DC.Description": [],
        "DC.Contributor": [],
        "DC.Coverage": [],
        "DC.Date": [],
        "DC.Type": [],
        "DC.Format": [],
        "DC.Source": [],
        "DC.Language": [],
        "DC.Relation": [],
        "DC.Identifier": [],
        "DC.Rights": [],
        "DC.Publisher": [],
        }

    meta_commands = []

    warnings = []
    address = None
    metafile = None

    def __init__(self, address=None):
        """Accept an address, which is a pointer to a page within the
        filesystem.
        """
        self.address = address

    def create_empty_metafile(self):
        """Return a string containing an empty metadata record.
        """
        metafile = ''
        return metafile

    def read_metafile(self):
        """Return a metadata structure from a text file.
        """
        pass

    def locate_metafile(self, filename):
        """Locate the metafile for the given filename.

        This follows this process:

        -   metafile in the parent directory.
        -   metafile in the meta directory.
        """
        pass
