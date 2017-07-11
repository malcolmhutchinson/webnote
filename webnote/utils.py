"""General utilities.

    Padding a number with leading zeros.
"""
def pad(input, length):
    """Pad a number with leading zeros.

    Given an input(int) and a length(int), return a string containing
    the input with leading zeros padded to length.

    """

    a = ""

    for i in range(0, length - len(str(input))):
        a += "0"

    a += str(input)

    return a
