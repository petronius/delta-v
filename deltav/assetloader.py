"""
Module for loading assets
"""

import os
import pyglet
import xmltodict

import deltav.configure
import deltav.system

def load_image(fname):
    """
    Return a Pyglet image object loaded from the file specified by <fname>
    """
    return pyglet.image.load(asset_path('images', fname))

def load_text(fname):
    """
    Load a text file and return its contents.
    """
    p = asset_path('text', fname)
    return open(p).read()

def load_fonts():
    """
    Install fonts so that Pyglet can use them.
    """
    fontsdir = os.path.join(deltav.system.DIR_ASSETS, 'fonts')
    for dirpath, dirnames, filenames in os.walk(fontsdir):
        for f in filenames:
            if not f.endswith('.ttf'):
                continue
            fontfile = os.path.join(dirpath, f)
            deltav.configure.logger.debug(" - loading %s" % fontfile)
            pyglet.font.add_file(fontfile)

def load_colordata():
    """
    Parse the colorscheme.xml asset and return the colors as a simplified Python
    dict.
    """
    f = os.path.join(deltav.system.DIR_ASSETS, 'colorscheme.xml')
    deltav.configure.logger.debug(" - loading %s" % f)
    outcolors = {}
    with open(f) as fd:
        d = fd.read()
        colordata = xmltodict.parse(d)
        palette = colordata.get('palette')
        colorsets = palette.get('colorset')
        for colorset in colorsets:
            if hasattr(colorset, 'items'):
                colors = colorset.get('color')
                for c in colors:
                    rgba = [int(i) for i in \
                                (c.get('@r'), c.get('@g'), c.get('@b'), '255')]
                    outcolors[c.get('@id')] = tuple(rgba)
    return outcolors

def asset_path(asset_type, filename):
    """
    Generic load function to simplify grabbing file paths by asset type.
    """
    path = os.path.join(deltav.system.DIR_ASSETS, asset_type, filename)
    if os.path.exists(path):
        return path
    else:
        return None
