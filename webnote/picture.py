"""webnote.picture classes.
"""

import datetime
import exifread
import os
import pytz

from PIL import Image

from directory import Directory
from metadata import Metadata
from webnote import Webnote

import settings


class Picture():
    """Analyse and process an image file.

    A picture is any image file, whether it can be displayed inline or
    not. This class will find and create viewable thumbnail copies at
    512 and 1024 pixels. It will supply the appropriate links and urls
    to have it displaying in a web page.

    """
    docroot = None
    address = None
    baseurl = None
    staticroot = None
    parent = None
    img = None
    exif_store = None
    
    def __init__(self, filename, docroot=None, baseurl=None,
                 data=None, staticroot=None):
        """
        """

        if not os.path.isfile(filename):
            raise self.FileNotFound(docroot)

        self.filename = filename
        (self.parentpath, self.fname) = os.path.split(filename)
        self.docroot = docroot
        self.baseurl = baseurl

        self.parent = Directory(
            self.parentpath, docroot=docroot, baseurl=baseurl
        )

        if not staticroot:
            staticroot = settings.STATIC_URL

        self.staticroot = staticroot
        self.data = data

        self.img = Image.open(filename)

    class FileNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)

    def __unicode__(self):
        return self.fname
        
    def __get_absolute_url__(self):

        address = self.filename.replace(self.docroot + '/', '')
        (path, fname) = os.path.split(address)
        (basename, ext) = os.path.splitext(fname)
        
        url = os.path.join(self.baseurl, path, 'picture', basename)

        return url
    
    url = property(__get_absolute_url__)


    def _get_img_src_(self):
        url = os.path.join(
            self.staticroot,
            self.filename.replace(
                self.docroot, self.staticroot + self.baseurl)
        )
        return url

    src = property(_get_img_src_)
    
    def alt(self):
        """Return the text in an tag alt attribute."""

        return self.fname

    def EXIFdatetime(self):
        """Date generated by the camera. TZ naive."""
        
        raw = str(self.read_exif()['Image DateTime'])
        dt = datetime.datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")

        #nztz = pytz.timezone('NZ')
        #dt = pytz.nz.localize()

#       Strip the UTC default timezone off. For some reason, this
#       still displays in the template when using the date filter.
        dt = dt.replace(tzinfo=None)
        
        return dt

    def GPSdatetime(self):
        """Return a datetime with timezone UTC from GPS data in EXIF.

        This is complicated by the curious structure returned by
        exifread. date and time are separate, and come in different
        formats. The time in particular comes as a cryptic 'instance',
        and the three values within it have to be converted first to
        string and then to integers.

        """
        

        if 'GPS GPSTimeStamp' in self.read_exif().keys():

            gpsdate = self.read_exif()['GPS GPSDate']
            gpstime = self.read_exif()['GPS GPSTimeStamp']

            UTC = pytz.timezone('UTC')
            (Y, M, D) = gpsdate.values.split(':')

            Y = int(Y)
            M = int(M)
            D = int(D)
            
            h = int(str(gpstime.values[0]))
            m = int(str(gpstime.values[1]))
            s = int(str(gpstime.values[0]))
            
            dt = datetime.datetime(Y, M, D, h, m, s, tzinfo=UTC)

            return dt

    def GPSaltitude(self):
        """Integer representation of the GPS altitudce from EXIF."""

        if 'GPS GPSAltitude' in self.read_exif().keys():
            
            (num, denom) = self.read_exif(
            )['GPS GPSAltitude'].printable.split('/')

            return float(num) / float(denom)

        return None
        
    def GPSlatitude(self):

        if 'GPS GPSLatitude' in self.read_exif().keys():
            (degs, mins, secs) = self.read_exif()['GPS GPSLatitude'].values
            (num, denom) = str(secs).split('/')
            degrees = float(str(degs))
            minutes = float(str(mins))
            seconds = (float(num) / float(denom))

            minsec = minutes + (seconds / 60)
            lat = degrees + (minsec / 60)

            if str(self.read_exif()['GPS GPSLatitudeRef']) == 'S':
                lat = lat * -1

            return lat
        
        return None

    def GPSlongitude(self):

        if 'GPS GPSLongitude' in self.read_exif().keys():
            (degs, mins, secs) = self.read_exif()['GPS GPSLongitude'].values
            (num, denom) = str(secs).split('/')
            degrees = float(str(degs))
            minutes = float(str(mins))
            seconds = (float(num) / float(denom))

            minsec = minutes + (seconds / 60)
            lon = degrees + (minsec / 60)
            return lon
        
        return None

    def fname1024(self):
        """Return a string filename to the 512px copy."""

        (basename, ext) = os.path.splitext(self.fname)
        return os.path.join(self.d1024(), basename + '_1024px' + ext.lower())
        
    def fname512(self):
        """Return a string filename to the 512px copy."""

        (basename, ext) = os.path.splitext(self.fname)
        return os.path.join(self.d512(), basename + '_512px' + ext.lower())
        
    def d1024(self):
        """Return the pathname to the 1024px directory."""

        d = os.path.join(
            self.parentpath,
            settings.FILEMAP_PICTURES['1024px'][0]
        )
        return d

    def d512(self):
        """Return the pathname to the 512px directory."""

        d = os.path.join(
            self.parentpath,
            settings.FILEMAP_PICTURES['512px'][0]
        )
        return d

    def gpxfiles(self):
        """Return a list of fienames for gpx files.

        Search the same directory this picture file is in.
        """
        
        return self.parent.model['gpx']
        
    def make_thumbnails(self):
        """Create thumbnail copies at 512 and 1024 pix."""


    def read_exif(self):
        """Return a dictionary of exif terms and values.

        It is necessary to read the file to get these data. In an
        effort to avoid doing this unnecesasriy, this method is not
        called on instantiation, and it has a read-once and store
        mechanism.

        """

        if self.exif_store:
            return self.exif_store
        
        f = open(self.filename, 'rb')
        self.exif_store = exifread.process_file(f)
        
        return self.exif_store
        
    def src1024(self):
        """Return a url to the 1024 px copy. """

        if os.path.isfile(self.fname1024()):
            url = os.path.join(
                self.staticroot,
                self.fname1024().replace(self.docroot, self.baseurl)[1:],
            )
                    
            return url

        return self.src

    def src512(self):
        """Return a url to the 512 px copy. """

        if os.path.isfile(self.fname512()):
            url = os.path.join(
                self.staticroot,
                self.fname512().replace(self.docroot, self.baseurl)[1:],
            )
                    
            return url

        return self.src

    def title(self):
        """A string containing a title."""

        return self.fname

 
