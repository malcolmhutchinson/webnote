Malcolm's webnote project
-------------------------

This is a collection of Python classes designed to analyse the
contents of a filesystem for text documents, and return structures
such that the documents can be easily displayed by a web server, and
linked with other documents within the filesystem.

It implements a simple filesystem syntax inspired by Dave Gruber's
Markdown, a syntax permitting easy writing for the web. The idea was
to expand markdown to include structuring collections of documents in
a filesystem of folders and subfolders, and using software in a
webserver to index them and provide links between them.

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

A full description of the simple syntax can be found in the
[wiki for this project](https://github.com/malcolmhutchinson/webnote/wiki/The-simple-syntax).


This repository contains Python classes for analysing directory
structures for readable files, inline images and metadata. It also
includes a Django project as a test implementation. The code files for
these two components are separated within the root directory into
`webnote/` and `djsrv/` respectively.


Further information is available in the [project wiki](https://github.com/malcolmhutchinson/webnote/wiki).

