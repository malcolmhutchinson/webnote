"""webnote.Gallery classes to handle directories of picture files.

"""

import os

from directory import Directory
from picture import Picture

import settings

class Gallery():

    dirpath = None
    docroot = None
    baseurl = None
    address = None
    gallery = None
    
    def __init__(self, docroot, baseurl, address):
        """Build the data structure describing this gallery."""

        dirpath = os.path.join(docroot, address)

        if not os.path.isdir(dirpath):
            raise self.DirectoryNotFound(dirpath)

        self.address = address
        self.baseurl = baseurl
        self.dirpath = dirpath
        self.docroot = docroot

        self.paired = Directory(dirpath, docroot=docroot, baseurl=baseurl)

    class DirectoryNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)
        
    def __get_absolute_url__(self):
        return os.path.join(self.baseurl, self.address)

    url = property(__get_absolute_url__)


    def gpxfiles(self):
        """Return the list of GPX file filenames."""

        return self.paired.model['gpx']

    def pictures(self, docroot=None, baseurl=None):
        """Return a list of picture objects."""

        pictures = []
        if not docroot:
            docroot = self.docroot
        if not baseurl:
            baseurl = self.baseurl
        
        for pic in self.paired.model['pictures']:
            fname = os.path.join(self.dirpath, pic)
            picture = Picture(fname, docroot=docroot, baseurl=baseurl)
            pictures.append(picture)

        return pictures

    
    def accession_pictures(self):
        """Process pictures into thumbnails.

        For each picture file 
        """

        warnings = []
        
        if not os.path.isdir(self.d1024()):
            warnings.append("Creating directory at " + self.d1024())
            os.mkdir(self.d1024())
        
        if not os.path.isdir(self.d512()):
            warnings.append("Creating directory at " + self.d512())
            os.mkdir(self.d512())

        warnings.extend(self.process_gps())

#        for picture in self.model['pictures']:
#            path = os.path.join(self.dirpath, picture)
#            if os.path.isfile(path):
#                print 'got one', path

        return warnings
    
    def processed(self):
        """True or false. Have the pictures here been processed?

        """

        for item in self.paired.model['dirs']:
            if item in settings.FILEMAP_PICTURES['1024px']:
                return True
            if item in settings.FILEMAP_PICTURES['512px']:
                return True

        return False
            
    def d1024(self):
        return os.path.join(
            self.dirpath, settings.FILEMAP_PICTURES['1024px'][0],
        )
    def d512(self):
        return os.path.join(
            self.dirpath, ssettings.FILEMAP_PICTURES['512px'][0],
        )

    def process_gps(self, pictime, gpstime, tzoffset):
        """Run gpscorrelate against gpx files found in this directory.
        """

        warnings = []

        warnings.append(
            "pictime " + str(pictime) + " " +
            str(gpstime) + " " + str(tzoffset))

        return warnings


        
