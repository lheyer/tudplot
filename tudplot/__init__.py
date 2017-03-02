import os

import numpy
import matplotlib as mpl
from matplotlib import pyplot
from cycler import cycler

from .xmgrace import export_to_agr, load_agr_data
from .tud import tudcolors, nominal_colors, sequentiell_colors


def activate(scheme='b', full=False, sequentiell=False, **kwargs):
    """
    Activate the tud design.

    Args:
        scheme (opt.): Color scheme to activate, default is 'b'.
        full (opt.):
            Activate the full color palette. If False a smaller color palette is used.
            If a number N is given, N colors will be chosen based on a interpolation of
            all tudcolors.
        **kwargs: Any matplotlib rc paramter may be given as keyword argument.
    """
    mpl.pyplot.style.use(os.path.join(os.path.dirname(__file__), 'tud.mplstyle'))

    if full:
        if isinstance(full, int):
            cmap = mpl.colors.LinearSegmentedColormap.from_list('tud{}'.format(scheme),
                                                                tudcolors[scheme])
            colors = cmap(numpy.linspace(0, 1, full))
        else:
            colors = tudcolors[scheme]
    elif sequentiell:
        colors = sequentiell_colors(sequentiell, scheme=scheme)
    else:
        colors = nominal_colors[scheme]

    mpl.rcParams['axes.prop_cycle'] = cycler('color', colors)


def saveagr(filename, figure=None, convert_latex=True):
    """
    Save the current figure in xmgrace format.

    Args:
        filename: Agrfile to save the figure to
        figure (opt.):
            Figure that will be saved, if not given the current figure is saved
    """
    figure = figure or pyplot.gcf()
    export_to_agr(figure, filename, convert_latex=convert_latex)


def markfigure(x, y, s, **kwargs):
    kwargs['transform'] = pyplot.gca().transAxes
    kwargs['ha'] = 'center'
    kwargs['va'] = 'center'
    kwargs.setdefault('fontsize', 'large')
    pyplot.text(x, y, s, **kwargs)


def marka(x, y):
    markfigure(x, y, '(a)')


def markb(x, y):
    markfigure(x, y, '(b)')
