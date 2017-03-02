import matplotlib as mpl
import numpy

tudcolors = {
    'a': ('#5D85C3', '#009CDA', '#50B695', '#AFCC50', '#DDDF48', '#FFE05C',
          '#F8BA3C', '#EE7A34', '#E9503E', '#C9308E', '#804597'),
    'b': ('#005AA9', '#0083CC', '#009D81', '#99C000', '#C9D400', '#FDCA00',
          '#F5A300', '#EC6500', '#E6001A', '#A60084', '#721085'),
    'c': ('#004E8A', '#00689D', '#008877', '#7FAB16', '#B1BD00', '#D7AC00',
          '#D28700', '#CC4C03', '#B90F22', '#951169', '#611C73'),
    'd': ('#243572', '#004E73', '#00715E', '#6A8B22', '#99A604', '#AE8E00',
          '#BE6F00', '#A94913', '#961C26', '#732054', '#4C226A'),
}


nominal_colors = {scheme: [tudcolors[scheme][i] for i in [1, 8, 3, 9, 6, 2]] for scheme in tudcolors}


def full_colors(N, scheme='b'):
    cmap = mpl.colors.LinearSegmentedColormap.from_list('tud{}'.format(scheme), tudcolors[scheme])
    return ['#{:02x}{:02x}{:02x}'.format(*cmap(x, bytes=True)[:3]) for x in numpy.linspace(0, 1, N)]


def sequentiell_colors(N, scheme='b'):
    cmap = mpl.colors.LinearSegmentedColormap.from_list('tud_h{}'.format(scheme), [tudcolors[scheme][i] for i in (0, 8)])
    return ['#{:02x}{:02x}{:02x}'.format(*cmap(x, bytes=True)[:3]) for x in numpy.linspace(0, 1, N)]
