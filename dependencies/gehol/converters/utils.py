__author__ = 'sevas'


def write_content_to_file(content, filename):
    """
    Simple function for writing string content to a disk file

    params:
    - content : content to write, as a string
    - filename : path to the output filename
    """
    fd = open(filename,'w')
    fd.write(content)
    fd.close()