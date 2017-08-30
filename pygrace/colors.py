import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict
from itertools import cycle


def make_cmap(colors, mapping=True):
    if isinstance(colors, dict):
        colors = np.array(colors.values())
    bit_rgb = np.linspace(0, 1, 256)
    position = np.linspace(0, 1, len(colors))
    _cols = colors[:] + 0 
    for i in range(len(colors)):
        for j in xrange(3):
            _cols[i][j] = bit_rgb[colors[i][j]]
    if mapping:
        cdict = {'red': [], 'green':[], 'blue':[]}
        for pos, color in zip(position, _cols):
            cdict['red'].append((pos, color[0], color[0]))
            cdict['green'].append((pos, color[1], color[1]))
            cdict['blue'].append((pos, color[2], color[2]))

        cmap = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 256)
    else:
        cmap = mpl.colors.ListedColormap(_cols, 'my_colormap')
    return cmap

cm_bw = OrderedDict([('white', (255, 255, 255, 1)),
                     ('black', (0, 0, 0, 1))])

cm_grace = OrderedDict([
    ('red',       (255, 0,   0,   255)),
    ('green',     (0,   255, 0,   255)),
    ('blue',      (0,   0,   255, 255)),
    ('yellow',    (255, 255, 0,   255)),
    ('brown',     (188, 143, 143, 255)),
    ('grey',      (220, 220, 220, 255)),
    ('violet',    (148, 0,   211, 255)),
    ('cyan',      (0,   255, 255, 255)),
    ('magenta',   (255, 0,   255, 255)),
    ('orange',    (255, 165, 0,   255)),
    ('indigo',    (114, 33,  188, 255)),
    ('maroon',    (103, 7,   72,  255)),
    ('turquoise', (64,  224, 208, 255)),
    ('green4',    (0,   139, 0,   255))
    ])


cm_tuda = OrderedDict([
    ('tud1a', (93,  133, 195, 255)),
    ('tud2a', (0,   156, 218, 255)),
    ('tud3a', (80,  182, 149, 255)),
    ('tud4a', (175, 204, 80,  255)),
    ('tud5a', (221, 223, 72,  255)),
    ('tud6a', (255, 224, 92,  255)),
    ('tud7a', (248, 186, 60,  255)),
    ('tud8a', (238, 122, 52,  255)),
    ('tud9a', (233, 80,  62,  255)),
    ('tud10a', (201, 48,  142, 255)),
    ('tud11a', (128, 69,  151, 255))
    ])

cm_tudb = OrderedDict([
    ('tud1b', (0,   90,  169, 255)),
    ('tud2b', (0,   131, 204, 255)),
    ('tud3b', (0,   157, 129, 255)),
    ('tud4b', (153, 192, 0,   255)),
    ('tud5b', (201, 212, 0,   255)),
    ('tud6b', (253, 202, 0,   255)),
    ('tud7b', (245, 163, 0,   255)),
    ('tud8b', (236, 101, 0,   255)),
    ('tud9b', (230, 0,   26,  255)),
    ('tud10b', (166, 0,   132, 255)),
    ('tud11b', (114, 16,  133, 255))
    ])

cm_tudc = OrderedDict([
    ('tud1c', (0,   78,  138, 255)),
    ('tud2c', (0,   104, 157, 255)),
    ('tud3c', (0,   136, 119, 255)),
    ('tud4c', (127, 171, 22,  255)),
    ('tud5c', (177, 189, 0,   255)),
    ('tud6c', (215, 172, 0,   255)),
    ('tud7c', (210, 135, 0,   255)),
    ('tud8c', (204, 76,  3,   255)),
    ('tud9c', (185, 15,  34,  255)),
    ('tud10c', (149, 17,  105, 255)),
    ('tud11c', (97,  28,  115, 255))
    ])
                
                    
cm_tudd = OrderedDict([
    ('tud1d', (36,  53,  114, 255)),
    ('tud2d', (0,   78,  115, 255)),
    ('tud3d', (0,   113, 94,  255)),
    ('tud4d', (106, 139, 55,  255)),
    ('tud5d', (153, 166, 4,   255)),
    ('tud6d', (174, 142, 0,   255)),
    ('tud7d', (190, 111, 0,   255)),
    ('tud8d', (169, 73,  19,  255)),
    ('tud9d', (156, 28,  38,  255)),
    ('tud10d', (115, 32,  84,  255)),
    ('tud11d', (76,  34,  106, 255))
    ])


def combine_maps(*args):
    color_map = OrderedDict()
    for d in args:
        for k, v in d.items():
            color_map[k] = v
    return color_map

cm_tud = combine_maps(cm_tuda, cm_tudb, cm_tudc, cm_tudd)

all_colors = combine_maps(cm_bw, cm_grace, cm_tud)

colors = cm_tud.values()

symbols = cycle(['o', 't', 'd', 's', '+'])

sym_map = {None: '0', 'o': '1', 's': '2', 'd': '3', 't': '6', '+': '9'}


class ColorDict(OrderedDict):
    def __init__(self, *args, **kwargs):
        super(ColorDict, self).__init__(*args, **kwargs)
        for d in [cm_bw, cm_tuda, cm_tudb, cm_tudc, cm_tudd, cm_grace]:
            old_length = len(self)
            for k, c in enumerate(d.keys()):
                rgb = d[c][:3]
                self[rgb] = (k + old_length, c)
        self._new = OrderedDict()

    def __contains__(self, item):
        if isinstance(item, tuple):
            return item in self.keys()
        elif isinstance(item. basestring):
            return any([item == v[1] for v in self.values()])
        else:
            return False

    def convert_color(self, color):
        c = tuple(color[0:3])
        if c not in self.keys():
            self[c] = (str(self.__len__()), ''.join('{:02X}'.format(a) for a in c))
            self._new[c] = (str(self.__len__()-1), ''.join('{:02X}'.format(a) for a in c))
        return self[c][0]

    def has_index(self, idx):
        return any([idx == v[0] for v in self.values()])

    def new_colors(self):
        return self._new

if __name__ == '__main__':
    pass
