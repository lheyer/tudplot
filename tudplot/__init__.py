import matplotlib
from matplotlib import pyplot
from .xmgrace import export_to_agr

matplotlib.use('Agg')

# Official TUD Colors
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
tudstyle = {
    'font.family': 'Charter',
    'lines.linewidth': 1.5,
    'lines.markeredgewidth': 1.5,
    'lines.markersize': 6,
    'figure.figsize': (6, 4),
    'markers.fillstyle': 'none',
}


def activate(scheme='b', full=True):
    """
    Activate a figure schems of the tud design.

    Args:
        scheme (opt.): Color scheme to activate, default is 'b'.
        small (opt.):
            Activate the full color palette. If False a smaller color palette is used.
    """
    import seaborn as sns
    sns.reset_defaults()
    if full:
        colors = tudcolors[scheme]
    else:
        colors = [tudcolors[scheme][i] for i in [0, 8, 10, 3, 6]]
    sns.set_palette(sns.color_palette(colors, len(colors)), len(colors))
    sns.set_style(tudstyle)
    # small_palette=sns.color_palette([colorsb[0], colorsb[8], colorsb[10],
    #                                   colorsb[3], colorsb[6]], 5)
    # full_palette=sns.color_palette(colorsc, len(colorsb))
# matplotlib.rcParams['markeredgecolor']  = 'none'


def saveagr(filename, figure=None):
    """
    Save the current figure in xmgrace format.

    Args:
        filename: Agrfile to save the figure to
        figure (opt.):
            Figure that will be saved, if not given the current figure is saved
    """
    figure = figure or pyplot.gcf()
    export_to_agr(figure, filename)
