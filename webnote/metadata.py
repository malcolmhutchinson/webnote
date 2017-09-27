"""Classes implimenting the simple filesystem syntax.
"""

import copy
import datetime
import os
import settings

class Metadata():
    """Provide services for dealing with metadata.

    This class knows all about the metadata files. Give it the
    pathname to a file and it will determine where the metafile is,
    read it and return a list of key/value pairs.

    It can also create a metafile for a new page, and guess the
    contents of certain fields, like title, author, etc.

    A metafile record looks like this:

        # Dublin Core metadata record
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
        DC.Publisher:   Malcolm Hutchinson
        DC.Relation:
        DC.Rights:      cc-by
        # END DC metadata

        # Page command options
        sort:           true
        deny:           all
        allow:          staff
        status:         draft
        # END page command

    This class takes a page address, which is the address generated by
    a Webnote object, pointing to a page (text or HTML file).

    This class can read a file containing a record like this, and
    parse it into a metadata structure.

    The metafile is represented by a list stored at
    self.filemodel, containing (key, value) tuples. These are
    obtained by splitting each line at the colon, and returning the
    first element as key, and a re-stitched list of the rest as value.

    """

    ELEMENTS = (
        "dc_title",
        "dc_creator",
        "dc_subject",
        "dc_description",
        "dc_contributor",
        "dc_coverage",
        "dc_date",
        "dc_type",
        "dc_format",
        "dc_source",
        "dc_language",
        "dc_relation",
        "dc_identifier",
        "dc_publisher",
        "dc_rights",
    )

    COMMANDS = (
        'status',
        'sort',
        'liststyle',
        'deny',
        'allow',
        'embargo',
    )

    warnings = []

    data = None
    filemodel = None
    metadata = None
    metafilename = None
    pagefile = None

    def __init__(self, pagefile=None, data=None):
        """Operations on metadata records.

        Instantiation creates a dictionary structure called
        `metadata`, holding lists of Dublin core elements, and
        commands.

        Initialise with an optional pathname to a page (without
        extension). Will search for a metafile under simple syntax
        rules, and read this file into the metadata structure.

        Initialise with data = a dictionary with those Dublin core and
        command keys, and it will load those values into the metadata
        structure.

        """

        metadata = self.build_empty_metadata()

        if pagefile:
            self.pagefile = pagefile
            self.metafilename = self.locate_metafile()
        else:
            self.pagefile = ''

        if self.metafilename:
            self.filemodel = self.read_metafile()
        else:
            self.metadata = metadata

        if self.filemodel:
            self.metadata = self.process_filemodel(self.filemodel)

        if data:
            self.data = data
            self.metadata = self.process_data(data)
        
    def build_empty_metadata(self):
        """Return an empty metadata structure dictionary. 

        This is a dictionary of lists, keyed by ELEMENTS and COMMANDS."""
        
        metadata = {}
        for element in self.ELEMENTS:
            metadata[element] = []
        for element in self.COMMANDS:
            metadata[element] = []

        return metadata

    def dublincore(self):

        """Return a list of DC metadata attribute names and values.

        List of (key, value) tuples taken from the metafile, with
        order and duplicated elements preserved.

        """

        dc = []

        for item in self.metadata.keys():
            if item[:3].lower() == 'dc_':
                dc.append(
                    (item.replace('dc_', 'DC.'),
                     '; '.join(self.metadata[item])))

        return dc

    def find_title(self):
        """Find the title from page content etc."""

        (path, fname) = os.path.split(self.pagefile)
        (basename, ext) = os.path.splitext(fname)
        title = basename.replace('_', ' ')

        return title

    def liststyle(self):
        """Determine the style of list from metafile """
        print "HERE"
        style = 'liststyles/simple.html'
        dir = 'liststyles/'
        ext = '.html'

        if 'list-style' in self.metadata.keys():
            return dir + self.metadata['list-style'] + ext

        return None

    def locate_metafile(self):
        """Locate the metafile for the given address.

        This follows this process:

        -   metafile in the parent directory.
        -   metafile in the meta directory.
        -   metafile in the paired directory.

        Return None if no file found.
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

    def formdata(self):
        """Return a dictionary suitable for populating forms."""

        formdata = {}
        
        for element in self.ELEMENTS:
            formdata[element] = '; '.join(self.metadata[element])
        for element in self.COMMANDS:
            formdata[element] = '; '.join(self.metadata[element])

        return formdata
        
    def metafile_record(self, data=None):
        """Return a string containing a metadata record in text format.

        This produces a string containing a record suitable for filing
        with pages in the document archive. It is intended to be
        written to a text file with a .meta suffix.

        If the metadata structure is empty, as at init, the result
        will be a file record with a list of keys, but no values.

        """

        record = '# Dublin core metadata.\n'

        metadata = self.metadata
        
        for element in self.ELEMENTS:
            if element in metadata.keys():
                key = element.replace('dc_', 'DC.')
                record +=  key + ": "
                record += '; '.join(metadata[element]) + '\n'

        record += "# end Dublin core elements.\n\n"

        record += "# Page commands.\n"
        for element in self.COMMANDS:
            if element in metadata.keys():
                record += element + ": "
                record += '; '.join(metadata[element]) + '\n'
        record += "# End page commands.\n"
        record += "# Record written by webnote.metadata at "
        record += str(datetime.datetime.now()) + '\n'

        return record

    def preferred_filename(self, fname=None):
        """Return the preferred filename for a new metadata file.

        """

        filename = ''
        (path, pagefile) = os.path.split(self.pagefile)

        if fname:
            filename = os.path.join(
                path, settings.META[0], fname.replace(' ', '_') + '.meta')
        else:
            (basename, ext) = os.path.splitext(pagefile)

            filename = os.path.join(
                path, settings.META[0], basename + '.meta')

        return filename

    def process_data(self, data):

        metadata = self.build_empty_metadata()

        for element in metadata.keys():
            if element in data.keys():
                metadata[element].append(data[element])

        return metadata
        
    def process_filemodel(self, filemodel):
        """Convert a filemodel into metadata structure.

        """

        metadata = self.build_empty_metadata()

        for line in self.filemodel:

            if line[0].lower() == 'comment':
                pass

            # Is the first element of the line a metadata key?
            elif line[0].lower().replace('.', '_') in metadata.keys():
                metadata[line[0].lower().replace('.', '_')].append(line[1])

            # Is it a command?
            elif line[0].lower() in self.COMMANDS:
                metadata[line[0]] = line[1]

            # Include one which isn't either a metadata element or a command.
            else:
                metadata[line[0]] = line[1]

        return metadata

    def read_metafile(self):
        """Return a metafile model structure from the metafile filename.

        Open and read the file, parse the contents into a filemodel
        structure.

        Key and value are separated by colon ':'.

        """

        metafilename = None
        record = [('filename:', self.metafilename)]

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

    def save(self, data=None):
        """Save a metarecord to file."""

        metafilename = None
        
        if data:
            self.metadata = self.process_data(data)

            if 'newfilename' in data.keys():
                fname = data['newfilename']
                metafilename = self.preferred_filename(fname)

        else:
            if self.metafilename:
                metafilename = self.metafilename

        if not metafilename:
            metafilename = self.preferred_filename()
            
        (path, fname) = os.path.split(metafilename)

        if not os.path.isdir(path):
            print "MAKING META DIRECTORY", path
            os.mkdir(path)

        record = self.metafile_record()        

        f = open(metafilename,'w')
        f.write(record)
        f.close()
        
#   Methods to return individual field values.    
    def title(self):
        return '\n'. join(self.metadata['dc_title'])

    def author(self):
        return '; '.join(self.metadata['dc_creator'])

    def contributors(self):
        return '; '.join(self.metadata['dc_contributor'])

    def description(self):
        return '\n'.join(self.metadata['dc_description'])

    def doctype(self):
        return '; '.join(self.metadata['dc_type'])

    def fileformat(self):
        return '; '.join(self.metadata['dc_format'])

    def language(self):
        return ', '.join(self.metadata['dc_language'])

    def location(self):
        return ', '.join(self.metadata['dc_coverage'])

    def pubdate(self):
        if len(self.metadata['dc_date']) > 0:
            return self.metadata['dc_date'][0]
        else:
            return ""

    def publisher(self):
        return '; '.join(self.metadata['dc_publisher'])

    def rights(self):
        return '; '.join(self.metadata['dc_rights'])
    
    def rights_markup(self):
        """Return marked-up code for rights. """
        rights = None
        right = '; '.join(self.metadata['dc_rights'])
        if right in settings.LICENSES.keys():
            rights = "<a href='" + settings.LICENSES[right][0] + "'>"
            rights += settings.LICENSES[right][1] + "</a>"

        return rights
        
    def source(self):
        return '; '.join(self.metadata['dc_source'])

    def sort(self):
        return self.metadata['sort'][0]

    def subject(self):
        return ', '.join(self.metadata['dc_subject'])

