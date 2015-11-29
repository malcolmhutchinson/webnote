"""Settings for the webnote application.

The SUFFIX structure captures file format extensions into a dictionary
with keys reflecting file type. It is this structure which provides
for the lists inside the directory object. 


References
----------

Dublin Core list of elements from
http://dublincore.org/documents/usageguide/elements.shtml

List of image format file extensions from 
http://en.wikipedia.org/wiki/Raw_image_format

Lists of Microsoft file formats from
https://en.wikipedia.org/wiki/List_of_Microsoft_Office_filename_extensions
https://en.wikipedia.org/wiki/Microsoft_Access#File_extensions

List of OpenDocument file format extensions from
https://en.wikipedia.org/wiki/OpenDocument

And a most comprehensive list of file formats at
https://en.wikipedia.org/wiki/List_of_file_formats

"""

DEBUG = True

META = ('meta/', )

THUMBNAILS = (
    'px128/',
    'thb',
)

INDEX_depreciated = {
    'filename': 'filename',
    'caption': 'caption',
    'description': 'description',
}

DC_ELEMENTS = (
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

CONTROL_ELEMENTS = (
    'sort-reverse',
    'allow',
    'deny',
    'status',
)



SUFFIX = {
    'archive': ('.gz','.tar', '.zip', ),
    'audio': ('.flac', '.mp2', '.mp3', '.wav', '.wma', ),
    'code': ('.c', '.cpp', '.py', ),
    'data': ('.csv', '.data', '.dat', '.dbf', ),
    'docs': ('.pdf',),
    'figs': ('.png', '.jpg', '.jpeg', '.gif', '.svg',),
    'geovector': (
        '.gml', '.gpx', '.kml', '.shp', '.tab',
    ),
    'html': ('.html', '.htm', '.xhtml',),
    'image': (
        '.3fr', '.ari', '.arw', '.bay', '.cap', '.cr2', '.crw', '.dcr',
        '.dcs', '.dng', '.drf', '.eip', '.erf', '.fff', '.iiq', '.k25',
        '.kdc', '.mdc', '.mef', '.mos', '.mrw', '.nef', '.nrw', '.orf',
        '.pef', '.ptx', '.pxn', '.r3d', '.raf', '.raw', '.rw2', '.rwl',
        '.rzw', '.sr2'  '.srf', '.srw', '.tif', '.tiff', '.x3f',
    ),
    'meta': ('.meta'),

    'ms_access': (
        '.ade', '.adp', '.adn', '.accdb', '.accdr', '.accdt',
        '.accda', '.mdb', '.cdb', '.cdb', '.mda', '.mdn', '.mdt',
        '.mdw', '.mdf', '.mde', '.accde', '.mam', '.maq', 
        '.mar', '.mat', '.maf', '.ldb', '.laccdb', 
    ),
    'ms_excel': (
        'xlsx', '.xlsm', '.xltx', '.xltm', '.xls', '.xlt', '.xlm',
        '.xlsb', '.xla', '.xlam', '.xll', '.xlw',  
    ),
    'ms_word': (
        '.doc', '.dot', '.docx', '.docm', '.dotx', '.dotm', '.docb',
    ),
    'opendoc_base': ('.odb',),
    'opendoc_formulae': ('.odf', ),
    'opendoc_graphics': ( '.odg', '.fodg', ),
    'opendoc_presentation': ('.opd', '.fodp', ),
    'opendoc_spreadsheet': ('.ods', '.fods', ),
    'opendoc_writer': ('.odt', '.fodt', ),


    'text': ('.txt', '.mkd',),
}
SUFFIX['page'] = SUFFIX['text'] + SUFFIX['html']
SUFFIX['microsoft_office'] = (
    SUFFIX['ms_access'] + SUFFIX['ms_excel'] + SUFFIX['ms_word'] )
SUFFIX['opendocument'] = (
    SUFFIX['opendoc_base'] +  SUFFIX['opendoc_formulae'] +
    SUFFIX['opendoc_graphics'] +  SUFFIX['opendoc_presentation'] +
    SUFFIX['opendoc_spreadsheet'] +  SUFFIX['opendoc_writer']
    )

DOCTYPE = (
    ('report', 'report'),
    ('note', 'note'),
    ('letter', 'letter'),
)

PAGE_STATUS = (
    ('working', 'working'),
    ('standing', 'standing'),
    ('PUBLIC', 'PUBLIC'),
)

TRUE = (
    'affirmative', 'affirm', 'aye', 'agree', 'agreed',
    'good', 'go',
    'indeed',
    'ok', 'okay', 'on',
    'right', 
    'sure',
    'true', 't',
    'up', 'white',
    'y', 'ya', 'yah', 'yeah', 'yes', 'yip', 'yep',
)

CREATIVE_COMMONS = {
    'cc-by': (
        'http://creativecommons.org/licenses/by/4.0/',
        'Creative Commons Attribution 4.0'),
    'cc-by-nc': (
        'http://creativecommons.org/licenses/by-nc/4.0/',
        'Creative Commons Attribution-NonCommercial 4.0'),
    'cc-by-sa': (
        'http://creativecommons.org/licenses/by-sa/4.0/',
        'Creative Commons Attribution-ShareAlike 4.0'),
    'cc-by-nc-sa': (
        'http://creativecommons.org/licenses/by-nc-sa/4.0/',
        'Creative Commons Attribution-NonCommercial-ShareAlike 4.0'),
    'cc-by-nd': (
        'http://creativecommons.org/licenses/by-nd/4.0/',
        'Creative Commons Attribution-NoDerivs 4.0'),
    'cc-by-nc-nd': (
        'http://creativecommons.org/licenses/by-nc-nd/4.0/',
        'Creative Commons Attribution-NonCommercial-NoDerivs 4.0'),

    'cc-by-nz': (
        'http://creativecommons.org/licenses/by/3.0/nz/',
        'Creative Commons Attribution New Zealand 3.0'),
    'cc-by-nc-nz': (
        'http://creativecommons.org/licenses/by-nc/3.0/nz/',
        'Creative Commons Attribution-NonCommercial New Zealand 3.0'),
    'cc-by-sa-nz': (
        'http://creativecommons.org/licenses/by-sa/3.0/nz/',
        'Creative Commons Attribution-NonCommercial-ShareAlike New Zealand 3.0'),
    'cc-by-nc-sa-nz': (
        'http://creativecommons.org/licenses/by-nc-sa/3.0/nz/',
        'Creative Commons Attribution-NonCommercial-ShareAlike New Zealand 3.0'),
    'cc-by-nd-nz': (
        'http://creativecommons.org/licenses/by-nd/3.0/nz/',
        'Creative Commons Attribution-NoDerivs New Zealand 3.0'),
    'cc-by-nc-nd-nz': (
        'http://creativecommons.org/licenses/by-nc-nd/3.0/nz/ 3.0',
        'Creative Commons Attribution-NonCommercial-NoDerivs New Zealand'),

}

LICENSES = CREATIVE_COMMONS

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
