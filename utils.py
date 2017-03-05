import os

def make_src(slug, filename=''):
    if filename:
        ext = filename.split('.')[-1]
    else:
        ext = ''
    src = "{}.{}".format(slug, ext)
    return os.path.join('gallery', src)
