"""Classes to implement the simple filesystem syntax.

The reference_figures() method in the parent class will return a text
string with figure references replaced with HTML IMG code linking the
inline image files in a given directory.

"""

import csv
import os
import settings
import re
import cgi


class Webnote():
    """Base class for the webnote application.

    Provide a method for processing a text string and list of figure
    files for figure references.

    Return (processed text, list of unreferenced figures).

    """

    warnings = []

    def reference_figures(self, source, prefix, directory=None, figures=None):
        """Convert coded references to figures in a text into HTML.

        Given a source text containing references to image files in
        the simple syntax format of:

            [[image.jpg Anything following the first space is a caption.]]

        And the name of a directory in which to find the image files,
        return a copy of the text with figure/caption references
        converted to a valid html div string, and a list of
        unreferenced figures. The HTML structure looks like:

            <div class='figure'>
                <img src='prefix/image.jpg' alt='image.jpg' />
                <p class='caption'>Anything following the first space
                is a caption.</p>
            </div>

        The prefix is prepended to the <img src> attribute to complete
        a working link.

        Optionally, the figures can be supplied as a list of filenames
        -- as found in the webnote parsed directory
        structure['figures']. Supplying this list will suppress
        calling the parse_directory method.

        An alternative syntax is:

            [[L:image.jpg Caption after first space...]]
            [[R:image.jpg Caption after first space...]]

        Making L/R: the first two characters will cause the output to
        change to:

            <div class='figure-left'> or
            <div class='figure-right'>

        ... as appropriate. You can style these to float left or right
        as necessary.

        ### Unimplemented

        We should be able to skip the image tagline if it has four
        spaces before it. This would be in keeping with the markdown
        syntax.

        """

        output = source
        unref = []
        links = []

        expression = r'\[\[.*\]\]'
        p = re.compile(expression)
        result = p.findall(source)

        if not figures:

            if self.figs:
                figures = self.figs
            elif directory:
                d = Directory(directory)
                figures = d.figs

        if figures:

            for figure in figures:
                link = os.path.join(prefix, figure)
                caption = figure
                unref.append((link, caption))

            for match in result:
                (link, html) = self._figure_html(match, prefix)
                output = output.replace(match, html)

                links.append(link)

                for fig in unref:
                    if fig[1] == link[0]:
                        unref.pop(unref.index(fig))

        return output, unref

    def _figure_html(self, match, prefix):
        """Replace a match code with the HTML DIV for displaying an image.

        - Strip off the square brackets at each end.
        - Break the remaining string by whitespace. The first of these
          will be the filename.
        - Put the remaining string back together.
        - Construct the HTML output string.
        """

        content = match.replace('[[', '')
        content = content.replace(']]', '')
        content = content.strip()
        divclass = 'figure'

        words = content.split(' ')
        filename = words.pop(0)

        if filename[:2] == 'L:':
            divclass = 'figure-left'
            filename = filename[2:]

        elif filename[:2] == 'R:':
            divclass = 'figure-right'
            filename = filename[2:]

        if prefix:
            filepath = os.path.join(prefix, filename)
        else:
            filepath = filename

        caption = ' '.join(words)
        caption = caption.strip()
        caption = cgi.escape(caption)

        link = (filename, caption)
        caption = caption.replace("'", "&#39;")

        html = "<div class='" + divclass + "'>\n"
        html += "    <img src='" + filepath + "' "
        html += "alt='" + filename + "' />\n"
        html += "    <p class='caption'>" + caption
        html += "</p>\n"
        html += '</div>\n\n'

        return (link, html)
