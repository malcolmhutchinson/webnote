"""Settings for the webnote application.

Dublin Core list of elements from:
http://dublincore.org/documents/usageguide/elements.shtml
"""

DEBUG = True

META = ('meta/', )

THUMBNAILS = (
    'img_128/', 
    'thb', 
)

INDEX = {
    'filename': 'filename',
    'caption': 'caption',
    'description': 'description',
}

DC_elements = (
    'DC.Title',
    'DC.Creator',
    'DC.Date',
    'DC.Subject',
    'DC.Description',
    'DC.Contributor',
    'DC.Coverage',
    'DC.Format',
    'DC.Identifier',
    'DC.Language',
    'DC.Publisher',
    'DC.Relation',
    'DC.Rights',
    'DC.Source',
    'DC.Type',
)

SUFFIX = {
    'data': ('.csv', '.data', '.dat'),
    'docs': ('.pdf',),
    'figs': ('.png', '.jpg', '.jpeg', '.gif', '.svg',),
    'html': ('.html', '.htm', '.xhtml',),
    'img_hires': (
        # This list taken from http://en.wikipedia.org/wiki/Raw_image_format
        '.3fr', '.ari', '.arw', '.bay', '.cap', '.cr2', '.crw', '.dcr',
        '.dcs', '.dng', '.drf', '.eip', '.erf', '.fff', '.iiq', '.k25',
        '.kdc', '.mdc', '.mef', '.mos', '.mrw', '.nef', '.nrw', '.orf', 
        '.pef', '.ptx', '.pxn', '.r3d', '.raf', '.raw', '.rw2', '.rwl',
        '.rzw', '.sr2'  '.srf', '.srw', '.tif', '.tiff', '.x3f',
    ),
    'meta': ('.meta'),
    'text': ('.txt', '.mkd',),
}
SUFFIX['page'] = SUFFIX['text'] + SUFFIX['html']

CREATIVE_COMMONS = {
    'cc-by': 'http://creativecommons.org/licenses/by/3.0/',
    'cc-by-nc': 'http://creativecommons.org/licenses/by-nc/3.0/',
    'cc-by-sa': 'http://creativecommons.org/licenses/by-sa/3.0/',
    'cc-by-nc-sa': 'http://creativecommons.org/licenses/by-nc-sa/3.0/',
    'cc-by-nd': 'http://creativecommons.org/licenses/by-nd/3.0/',
    'cc-by-nc-nd': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',

    'cc-by-nz': 'http://creativecommons.org/licenses/by/3.0/nz/',
    'cc-by-nc-nz': 'http://creativecommons.org/licenses/by-nc/3.0/nz/',
    'cc-by-sa-nz': 'http://creativecommons.org/licenses/by-sa/3.0/nz/',
    'cc-by-nc-sa-nz': 'http://creativecommons.org/licenses/by-nc-sa/3.0/nz/',
    'cc-by-nd-nz': 'http://creativecommons.org/licenses/by-nd/3.0/nz/',
    'cc-by-nc-nd-nz': 'http://creativecommons.org/licenses/by-nc-nd/3.0/nz/',

}

LICENSES = CREATIVE_COMMONS
