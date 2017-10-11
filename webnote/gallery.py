"""webnote.Gallery classes to handle directories of picture files.

Probably obsolete.
"""

import os

class Gallery():
    
    docroot = None
    baseurl = None
    address = None
    gallery = None
    
    FILEMAP = {
        'original': ('raw',),
        '1024px': ('view',)
    }
    
    def __init__(self, docroot, baseurl, address):
        """Build the data structure describing this gallery."""
        
        directory = os.path.join(docroot, address)
        url = os.path.join(baseurl, address)
        
        if not os.path.isdir(directory):
            raise self.DocrootNotFound(docroot)
            
        self.gallery = self._scan_directory(directory)
        
    class DocrootNotFound(Exception):
        def __init__(self, value):
            self.value = value

        def __str__(self):
            return repr(self.value)
        
    def get_absolute_url(self):
        return os.path.join(self.baseurl, self.address)

    url = property(get_absolute_url)
    
    def _scan_directory(self, path):
        if not os.path.isdir(path):
            return None

        result = {}
        for item in os.listdir(path):            
            itempath = os.path.join(path, item)

            if os.path.isfile(itempath):
                (path, fname) = os.path.split(itempath)
                (basename, ext) = os.path.splitext(fname)
                (discard, parent) = os.path.split(path)

                copy = None
                for thing in self.FILEMAP:
                    if parent in self.FILEMAP[thing]:
                        copy = thing
                
                if basename in result.keys():
                    result[basename] = itempath
                else:
                    result[basename] = {copy: itempath}
                                        
            elif os.path.isdir(itempath):
                    
                nextdir = self._scan_directory(itempath)

                # Iterate the resulting dictionary of basenames.
                for key in nextdir.keys():
                    if key in result.keys():
                        result[key].update(nextdir[key])
                    else:
                        result[key] = nextdir[key]

        return result   
