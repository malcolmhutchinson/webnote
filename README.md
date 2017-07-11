The simple syntax
=================

The simple syntax is a way of organising files and folders within a
directory structure, such that text and html documents can be used to
index collections of pages and image files. It employs the
hierarchical nature of a filesystem to group documents together and
automatically index them.

It was inspired by Dave Gruber's Markdown, a syntax permitting easy
writing for the web. The idea was to expand markdown to include
structuring collections of documents in a filesystem of folders and
subfolders, and using software in a webserver to provide links between
them.

The simple syntax provides for a set of predictable filenames which
are human- and machine-readable, and which relate text or html
documents to other files, like images and figures. 

For example, if you want to start writing a book, you would create a
folder called `MyBook`. Into this folder, you create text files for
each of the chapters of the book. When you visit _MyBook_ in a
browser, you would see a list of the chapters, with links so you can
visit each chapter.

The syntax is designed to be implemented in a web server, providing a
way of automatically linking related pages together. An important
consideration, however, is that the archive can be read without the
software. Written material is stored as ASCII-encoded text (or UTF-8,
or Unicode, or any text encoding). Image files used as figures in the
text are kept in predictable locations, and can be viewed with an
image viewer. Files can be edited directly with a text editor, or with
forms provided by the webnote webserver software.

Convenient means of attaching metadata to documents and files is also
provided. 



Preamble
--------

This is a syntax of filesystem file names. The central idea is that
files with the same basename relate to each other. So, a file called
`journal.txt` relates to a folder called `journal/`.  The file
`journal.txt` and the folder `journal/` are said to be paired.

In this syntax, any file which can contain written information in
text, or encoded in HTML, is called a page. Some pages stand by
themselves, others have files -- figures or more pages -- associated
with them. If a page refers to figures in its text, those figures will
be stored as image files in the paired folder.

The syntax includes special filenames for metadata files, and the
directories they can be stored in. A file called `journal.meta` in one
of a selection of locations will contain metadata for the text file
`journal.txt`. Metadata files contain a list of Dublin Core metadata
elements, and may contain commands to affect the way the text file and
its associated files are displayed.

Folders with nothing but image files in them can also be automatically
indexed. Clicking on the link to an image file will produce a page
displaying the image, and summarising what is known about it,
including any metadata files written for it.

The whole collection of files conforming to the simple syntax is
called an archive. It starts at a document root, or `docroot`.


### Example file structure

Within a given directory, 

    path/to/dir/               This is the docroot. It is also the
                               name of the archive.
        blog/                  The name of a chapter or section.
            entry1.txt
            entry2.txt
            entry3.txt
            img1.jpg
            img2.jpg
        blog.txt

The file `blog.txt` is the page owning the files in the directory
`blog/`. It is the parent of pages in that directory. The machine will
present the contents of the file, and then a list of page files within
the directory:

    Contents of the file blog, which may be any text and may be
    intended to be marked down. It may also contain html code and
    references to image files in the directory paired with this file.

    -- (hr) ------------------------------------------------------------

    Heading stating "unreferenced images"

        image link to the file `blog/img1.png`

        image link to the file `blog/img2.png`

    Heading stating "contents"

        List of page files in the directory `blog`.

In this way a section or division within the filespace can be created
by making a directory and a .txt file with the same basename.

Any images to be displayed with the file, either referred to in the
text or listed as unreferenced images below it, will be looked for in
the directory paired with the file.



The rules
---------


### Nomenclature

An _archive_ is a filesystem below a particular directory (the
_docroot_) in which the files conform to the naming conventions
specified in the simple syntax.

A _page_ is a text or html file. The contents of a page are intended
to be displayed in a browser.

Being a file, a page exists in a directory, and it may have
_siblings_.  Siblings are other pages in the same directory.

A page may also have _children_. These are pages in a directory with
the same basename as the file (the paired directory). This directory
may contain more pages, or it may have image files or document files
or a combination of any. All of the files in this directory are owned
by the text file with the same basename as the directory.

A page may have a _metafile_ associated with it. This is a text file
with the same basename and the suffix `.meta`. It is found in one of
three place (listed below). The metafile stores a Dublin Core list of
elements, and commands affecting the way the page and its children
behave.

A page's children will usually be sorted alphanumerically by file
name. The order can be affected by commands in the metadata file.

A page is called by an _address_ which is conveyed from the browser as
a URL. The address points to the page file and is translated into a
full filesystem path.


### Example filesystem 

    path/to/dir/               Document root (docroot).
        blog/                  Directory pared with blog.txt.
            entry1/            Directory paired with blog/entry1.txt.
                image1.jpg     Image refered to in blog/entry1.txt.
                image2.jpg     Image refered to in blog/entry1.txt.
            entry2/            Directory paired with blog/entry2.txt.
                image3.jpg     Image refered to in blog/entry2.txt.
                image4.jpg     Image refered to in blog/entry2.txt.
            meta/              Metadata for children of blog.txt.
                entry1.meta    Metadata for blog/entry1.txt.
                entry2.meta    Metadata for blog/entry2.txt.
                entry3.meta    Metadata for blog/entry3.txt.
            entry1.txt         Blog entry - text content.
            entry2.txt         Blog entry - text content.
            entry3.txt         Blog entry - text content.
            img5.jpg           Image refered to in blog.txt.
            img6.jpg           Image refered to in blog.txt.
        blog.meta              Metadata file for blog.txt.
        blog.txt               Introduction to blogs - text content.


### Inserting figures

A figure is any image file in the paired folder of a type which can be
displayed in a browser. This includes .jpg, .png, and .svg files.

Any such file can be inserted at any point in the text by encodng a
link including the filename and a caption, encased in double square
brackets:

    [[filename.png Everything after the first space is a caption.]]

This will be translated into the following HTML:

    <div class='figure'>

        <img src='url/to/filename.png' alt='filename.png' >

        <p class='caption'>Everything after the first space is a caption.</p>

    </div>

You can cause the image file to be displayed as a float to the left or
right by preceeding the filename with the code `L:` or `R:`, This
renames the enclosing `<div>` tag with `class=figure-left` or
`class='figure-right`.

    [[L:filename.jpg Everything after the first space is a caption.]]

Will be rendered as

    <div class='figure-left'>

        <img src='url/to/filename.png' alt='filename.png' >

        <p class='caption'>Everything after the first space is a caption.</p>

    </div>


### Relationships

- A page has a parent page.
- A page exists in a parent directory.
- A page may have a paired directory.
- A page may have a metafile.
- A page may have siblings; other pages in its parent directory.
- A page may have children; pages in its paired directory.

Next and previous links are found amongst the page's siblings. This is
usually the simple sort order, but may be controlled by lines in the
file's metafile.


### File types

When a directory is scanned, the file contents are sorted according to
type, with these types identified:

    data           Files ending with .dat, .csv etc.
    doc            PDF and other document formats.
    figure         Any inline image format, including JPG, SVG, PNG etc.
    html           A text-encoded file containing HTML.
    img_hires      TIFF and other image files not inline-able.
    meta           Metadata files. 
    text           A text document intended for markdown.

Data files can be used to index directories of filenames.

Documents and high-res image files can be indexed, with links provided
to download.

Figures can be referred to by a code in the text, providing a caption
with the link to the image files. Any "figure" files not referred to
in the text can be listed at the end of that text.

### Search locations

When searching for expected associated files, finding one causes the
machine to stop looking. That is, the first one it finds will be used. 

Metafile: 

1.  In the file's parent directory (same directory as the file itself).
1.  In a directory called `meta` in the file's parent directory.
1.  In the file's paired directory.

Image index file

1.  In the same folder as the collection of images.
1.  Filename can be _anything_`.csv`.


Special case: the document root
-------------------------------

The document root is necessarily a special case, because it doesn't
have a parent directory. The `docroot` is the top-level address for a
web application which uses the simple syntax, and so there is no "up"
from here. The children of the docroot are the siblings; all pages in
the document root directory.

Pointing the browser at the docroot should display the contents of an
index file. This should be called `index.txt` or `index.html` and be
in the document root directory.

The index will not appear on the list of docroot siblings.

In this case, the siblings become the first-level divisions of the
archive. You might have "MyBook" as one of these divisions,
"FieldNotes" as another.


Images & figures
----------------

Any image files of type png, jpg, gif, svg, which can be displayed
inline, can be put into the paired directory, and will be
displayed with the paired file.

    gallery
        img_1024/
            img1.jpg  } High resolution
            img2.jpg  }
            img3.jpg  }
        img1.jpg      } Low resolution
        img2.jpg      }
        img3.jpg      }
        captions.csv
    gallery.txt

Requesting `gallery/` as a URL should display the contents of the file
`gallery.txt`, with any referenced images displayed inline in the
text. Any unreferenced images will be displayed in sorted order below
the text.

If the text file `gallery.txt` is absent, the images in the directory can
be displayed as a list of filenames, with whatever data is available from
the exif set, and from any meta file present in the directory.

The file `captions.csv` contains at least two columns, being
`filename` and `caption`. It can be called anything ending in
`.csv`. The machine will use the first CSV file it finds.

If a CSV file is present, and if it contains those two columns, it
will be used to supply captions with images. 

The directory `img_1024` is optional. Any directory begining with
`img_` will be searched for filenames corresponding to the files in
the current directory. This is used to keep high-resolution copies of
figures and image files which can be displayed separately on request.

If more than one directory with this prefix is found, more policy will
have to be written.


### CSV syntax

The first file with a suffix `.csv` found in the directory will be
used to index the images there. It may have the following columns --
an asterisk denotes the column is required.

    filename  *      The image filename.
    caption   *      Short text line.
    title            Title to use when presenting the image.

There may be scope for including Dublin Core fields in this index
file, also.



Metadata
--------

Metadata for a given text file can be stored in a file with a `.meta`
suffix. The machine will search for a file named `blog.meta` in the
file's parent directory, in a directory called `meta` in the
parent directory, and in the file's paired directory. 

    path/to/dir/
        blog/
            entry1/
                img1.jpg
                img2.jpg
            entry1.txt
            entry2/
                entry2.meta
            entry2.txt
            entry3.txt
            img3.jpg
            img4.jpg
            meta/
                entry1.meta
        blog.meta
        blog.txt

In the example filespace above, metadata for the file `blog.txt` is
found in the parent directory, so we stop looking when we find
that. The metadata file for `entry1.txt` will not be found in the same
directory as the file, so we then look in the directory called `meta`
within that same directory. We find it there and stop
looking. Metadata for the file `entry2.txt`, however, hasn't been
found in either of those places, so the last place we look is in the
paired directory.

The metafile is always called `[basename].meta`.

Metadata files contain a rendering of the Dublin Core Metadata set,
and certain commands, such as sorting in reverse order.

Any inline files found in a paired directory will be displayed inline
below the text from the paired file, unless referenced with the
[filename caption]] syntax in the contents of the text file.



Implimentation in Python
------------------------

There are four classes:

1.  The superclass `Webnote` provides the
    `reference_figures()` method, which searches the text for the figure
    reference code and replaces it with HTML code.

2.  The 'Directory' class, subclasses `Webnote`. This scans a given
    directory, providing for lists of files by type, and giving access
    to the `reference_figures()` method from the parent class.

3.  The `Page` class, which provides all the methods associated with
    displaying a page, including computing parent and sibling pages,
    next and previous, and linking to other files in the paired
    folder.

4.  The `Metadata` class, which provides all computations associated
    with metadata, including finding and reading metadata files, and
    outputting metadata in HTML and other formats.
