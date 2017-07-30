"""Classes implimenting the simple filesystem syntax.
"""

import os
import settings

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
    metarecord = None
    metastructure = None
    metadata = None
    commands = None

    def __init__(self, pagefile, prefix=None):
        """Operations on metadata records.

        Initialise with a file pathname.
        """

        self.pagefile = pagefile
        self.prefix = prefix

        self.metadata = self.dc_metadata.copy()
        self.metadata.update(self.meta_commands)

        self.metafilename = self._locate_metafile()

        if self.metafilename:
            self.metadata['filename'] = self.metafilename
            self.metarecord = self._read_metafile()

        if self.metarecord:
            (self.metadata, self.commands) = self.process_metarecord()

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

    contributor = property(_contributor)

    def _location(self):
        return ', '.join(self.metadata['dc.coverage'])

    location = property(_location)

    def _rights(self):
        return '; '.join(self.metadata['dc.rights'])

    rights = property(_rights)

    def _source(self):
        return '; '.join(self.metadata['dc.source'])

    source = property(_source)
