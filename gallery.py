"""webnote.Gallery classes to handle directories of picture files.

"""

import datetime
import os
import pytz
import subprocess

from directory import Directory
from picture import Picture
from PIL import Image

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

        for picture in self.paired.model['pictures']:
            path = os.path.join(self.dirpath, picture)
            (basename, ext) = os.path.splitext(picture)
            f1024 = basename + '_1024px' + ext.lower()
            path1024 = os.path.join(self.dirpath, self.d1024(), f1024)
            f512 = basename + '_512px' + ext.lower()
            path512 = os.path.join(self.dirpath, self.d512(), f512)
            if os.path.isfile(path):
                i = Image.open(path)
                i.thumbnail((1024, 1024))
                i.save(path1024, "jpeg")
                i.thumbnail((512, 512))
                i.save(path512, "jpeg")

        warnings.append("Creating thumbnail copies.")

        return warnings

    def processed(self):
        """True or false. Have the pictures here been processed?

        This looks for the presence of subdirectories with names
        appearing in settings.FILEMAP_PICTURES.

        """

        for item in self.paired.model['dirs']:
            if item in settings.FILEMAP_PICTURES['1024px']:
                return True
            if item in settings.FILEMAP_PICTURES['512px']:
                return True

        return False

    def d1024(self):
        """Pathname to 1024px directory."""
        return os.path.join(
            self.dirpath, settings.FILEMAP_PICTURES['1024px'][0],
        )

    def d512(self):
        return os.path.join(
            self.dirpath, settings.FILEMAP_PICTURES['512px'][0],
        )

    def process_gps(self, pictime, gpstime, tzoffset):
        """Run gpscorrelate against gpx files found in this directory.

        pictime will be naive, gpstime will be UTC.

        First, convert the picture time to UTC using the timezone
        offset. Then compute the difference in time between the photo
        and gps time signatures. With these data, you can compose the
        gpscorrelate command to be run in a shell.

        The variable tzoffset is expected as a string in the manner of
        '+1200'.

        From the man gpscorrelate page:

        gpscorrelate [-z | --timeadd +/-HH[:MM]] [-O | --photooffset seconds]
                    [-i | --no-interpolation] [-v | --verbose] [-d |
                    --datum datum] [-n | --no-write] [-m | --max-dist time]
                    [-t | --ignore-tracksegs] [-M | --no-mtime] [-f |
                    --fix-timestamps] [-p | --degmins] -g file.gpx
                    image.jpg...

       -O, --photooffset seconds
           time in seconds to add to the photo timestamp to make it match the
           GPS timestamp. To determine the amount of seconds needed, just
           create a picture of your GPS device showing the current time and
           compare it with the timestamp of your photo file.

        """

        warnings = []

        if not gpstime:
            warnings.append("GPS time required.")
            warnings.append("No correlation performed.")
            return warnings

        if not tzoffset:
            warnings.append("Timezone offset required.")
            warnings.append("No correlation performed.")
            return warnings

        photooffset = pictime - gpstime
        photooffset = photooffset.seconds

        if gpstime < pictime:
            photooffset = photooffset * -1

#       Process tzoffset into HH:MM.
        h = tzoffset[:3]
        m = tzoffset[-2:]

        Z = h + ':' + m

#       Provide a list of picture file extensions.
        extensions = []
        for thing in self.paired.model['pictures']:
            (basename, ext) = os.path.splitext(thing)
            if ext not in extensions:
                extensions.append(ext)

#       Compile a list of gpscorrelate commands.
        precom = "gpscorrelate -M -z " + Z + " "
        precom += "-O " + str(photooffset) + " "
        precom += "-g "

        commands = []
        for gpxfile in self.gpxfiles():

            gpxfname = os.path.join(
                self.dirpath, gpxfile.replace(' ', '\ ')
            )
            command = precom + gpxfname

            for ext in extensions:
                fullcommand = command + " " + self.dirpath + "/*" + ext

                commands.append(fullcommand)

#       Execute the commands and return the output.
        outputs = []
        os.chdir(self.dirpath)
        for line in commands:

            try:
                output = subprocess.check_output(line, shell=True)

            except subprocess.CalledProcessError:
                output = "Something went wrong. No correlation was performed."

            outputs.append("<pre>" + output + "</pre>")

        return outputs
