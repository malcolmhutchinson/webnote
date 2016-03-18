"""Classes to implement the simple filesystem syntax.

This module provides Page, Directory and Metadata classes. Objects
from the Page class process individual page files, providing links to
parents, siblings and children, and processing test strings for image
references.

The directory class will analyse a directory listing, providing lists
of files sorted by type. It has methods for computing lists of links
to files within the given directory.

The Metadata class performs all functions on a page's metadata,
including locating files, reading them into memory structures, and
providing standard outputs.

"""

import csv
import os
import settings
import re
import cgi
#import pypandoc
import markdown2 as markdown


class Webnote():
    """Base class for the webnote application.

    Provide a method for processing a text string and list of figure
    files for figure references.

    Return (processed text, list of unreferenced figures).

    """

    warnings = []

    def reference_figures(self, source, prefix, directory=None, figures=None):
        """Convert coded references to figures in a text into HTML.

        Given a source text containing references to image files in
        the simple syntax format of:

            [[image.jpg Anything following the first space is a caption.]]

        And the name of a directory in which to find the image files,
        return a copy of the text with figure/caption references
        converted to valid html, and a list of unreferenced figures.

        The prefix is appended to the <img src> attribute to complete
        the link.

        Optionally, the figures can be supplied as a list of filenames
        -- as found in the webnote parsed directory
        structure['figures'] structure. Supplying this list will
        suppress calling the parse_directory method.

        ### Unimplemented

        We should be able to skip the image tagline if it has four
        spaces before it. This would be in keeping with the markdown
        syntax.

        """

        output = source
        unref = []
        links = []

        expression = r'\[\[.*\]\]'
        p = re.compile(expression)
        result = p.findall(source)

        if not figures:

            if self.figs:
                figures = self.figs
            else:
                d = Directory(directory)
                figures = d.figs

        for figure in figures:
            link = os.path.join(prefix, figure)
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

        html = "<div class='figure'>\n"
        html += "    <img src='" + filepath + "' "
        html += "alt='" + filename + "' />\n"
        html += "    <p class='caption'>" + caption
        html += "</p>\n"
        html += '</div>\n\n'

        return (link, html)

            
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

        if settings.DEBUG:
            print "--> webnote.Directory.parse_directory"

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

        if settings.DEBUG:
            print "--> webnote.Directory._get_figs"
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
        parent     Page object to the parent page.
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

    def __init__(self, docroot, address=None, prefix=None):
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
            for item in self.parent_directory.pages:

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

        #return self._store_title

    title = property(_get_title)

    def _get_content(self):
        """Compute the content string.

        This will be returned a HTML code, either direct from an HTML
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
        prefix = os.path.join('/static', self.address)
        figures = None

        if self.paired_directory:
            figures = self.paired_directory.figs
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

    content = property(_get_content)

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
            self._store_parent = (prefix , 'Index') 
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
        
        #kids = self.paired_directory.link_pages(prefix)

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
            #'dc_contributor': self.metadata.contributor,
            'dc_coverage': self.metadata.location,
            'dc_rights': self.metadata.rights,
            'dc_source': self.metadata.source,
            #'dc_type': self.metadata.type,
        }

        return data


class Metadata():
    """Provide services for dealing with metadata.

    This class knows all about the metadata files. Give it the
    pathname to a file and it will determine where the metafile is,
    read it and return a dictionary of key/value pairs.

    It can also write a metadata file, given a list containing lines
    to be written into the file. Each item in the list is a (key,
    value) tuple.

    A metadata record looks like this:

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

        # Page command options
        sort-reverse:   false # true
        deny:           all
        allow:          staff
        status:         draft
        # END page command

    This class takes a page address, which is the address generated by
    a Webnote object, pointing to a page (text or HTML file).

    This class can read a file containing a record like this, and
    parse it into a metadata structure.

    This file is represented by a list containing (key, value)
    tuples. These are obtained by splitting each line at the colon,
    and returning the first element as key, and a re-stitched list of
    the rest as value.

    The gist of the thing is a metastructure like this:

        metadata = {
            'dc_title': [],
            ...  
            'status': [],
            ...
        }

    These two variables are defined as a dictionary of DC elements,
    and a list of commands.

    """

    dc_metadata = {
        "dc.title": [],
        "dc.creator": [],
        "dc.subject": [],
        "dc.description": [],
        "dc.contributor": [],
        "dc.coverage": [],
        "dc.date": [],
        "dc.type": [],
        "dc.format": [],
        "dc.source": [],
        "dc.language": [],
        "dc.relation": [],
        "dc.identifier": [],
        "dc.rights": [],
        "dc.publisher": [],
    }

    meta_commands = {
        'status': [],
        'sort-reverse': [],
        'deny': [],
        'allow': [],
        'embargo': [],
    }

    warnings = []

    pagefile = None
    prefix = None
    metafilename = None
    metarecord = None    # List of (key, value) tuples rep. the file.
    metastructure = None # Dictionary containing metadata.
    metadata = None
    commands = None


    def __init__(self, pagefile, prefix=None):
        """Operations on metadata records.

        Initialise with a file pathname.
        """

        self.pagefile = pagefile
        self.prefix = prefix

        self.metadata =  self.dc_metadata.copy()
        self.metadata.update(self.meta_commands)

        self.metafilename = self._locate_metafile()

        if self.metafilename:
            self.metadata['filename'] = self.metafilename
            self.metarecord = self._read_metafile()

        if self.metarecord:
            (self.metadata, self.commands)  = self.process_metarecord()

    def save(self, data):
        """Replace the contents of the meta file with items data.
        """

        self.construct_metafile()

        return True

    def update_metadata(self, data):
        """Replace values in the metadata structure with supplied dictionary.

        This is often used with POST data.
        """

        return True

            
    def construct_metafile(self):
        """Return a string containing a metadata record in text format.

        This produces a string containing a record suitable for fileing
        with pages in the document archive. It is intended to be
        written to a text file with a .meta suffix.

        If the metadata structure is empty, as at init, the result
        will be a file record with a list of keys, but no values.

        """
        metarecord = ''

        #for item in self.metadata:
        #    print item
        
        return metarecord

    def _locate_metafile(self):
        """Locate the metafile for the given address.

        This follows this process:

        -   metafile in the parent directory.
        -   metafile in the meta directory.
        """

        (basename, ext) = os.path.splitext(self.pagefile)
        
        filename = basename + '.meta'

        if os.path.isfile(filename):
            return filename

        steps = basename.split('/')
        last = steps.pop()
        path = '/'.join(steps)
        metaname = last + '.meta'

        filename = os.path.join(path, 'meta', last + '.meta')

        if os.path.isfile(filename):
            return filename

        filename = os.path.join(basename, metaname)
        if os.path.isfile(filename):
            return filename

        return None

    def _read_metafile(self):
        """Return a metadata structure from the metafile filename.

        Open and read the file, parse the contents into a metadata structure.
        """

        record = [('filename', self.metafilename)]

        with open(self.metafilename) as f:
            contents = f.readlines()

        for line in contents:
            if line[0] == '#':
                key = 'comment'
                value = line[1:]
                record.append((key, value))
            else:
                bits = line.split(":")
                key = bits.pop(0)
                key = key.strip()
                value = ':'.join(bits)
                value = value.strip()
                record.append((key, value))

        return record

    def process_metarecord(self):
        """Turn a file record thing into a memory structure we can work with.

        """

        metadata = {}
        commands = self.meta_commands

        for element in settings.DC_ELEMENTS:
            metadata[element.lower()] = []
        
        for line in self.metarecord:
            
            if line[0].lower() in metadata.keys():
                metadata[line[0].lower()].append(line[1])

            elif line[0] in commands:
                commands[line[0]] = line[1]

        return (metadata, commands)
    
    def _title(self):
        return '\n'. join(self.metadata['dc.title'])

    title = property(_title)

    def _author(self):
        return '; '.join(self.metadata['dc.creator'])

    author = property(_author)

    def _date(self):
        if len(self.metadata['dc.date']) > 0:
            return self.metadata['dc.date'][0]
        else:
            return ""
        
    date = property(_date)

    def _subject(self):
        return ', '.join(self.metadata['dc.subject'])

    subject = property(_subject)

    def _description(self):

        desc = """This fake description is declared in the
        webnote. Metadata._description() method."""

        return '\n'.join(self.metadata['dc.description'])

    description = property(_description)

    def _contributor(self):
        return '; '.join(self.metadata['dc.contibutor'])

    contirbutor = property(_contributor)

    def _location(self):
        return ', '.join(self.metadata['dc.coverage'])

    location = property(_location)

    def _rights(self):
        return '; '.join(self.metadata['dc.rights'])

    rights = property(_rights)

    def _source(self):
        return '; '.join(self.metadata['dc.source'])

    source = property(_source)


