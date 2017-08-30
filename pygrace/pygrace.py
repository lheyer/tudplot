import numpy as np
from matplotlib.colors import ColorConverter
from matplotlib.backends import backend_agg
import matplotlib.pyplot as plt
import textwrap
from itertools import zip_longest
from collections import defaultdict

from . import tex2grace
from .tex2grace import latex_to_xmgrace


def update_labels(labels, axis=None):
    if axis is None:
        axis = plt.gca()
    for line, lb in zip_longest(axis.lines, labels, fillvalue=''):
        line.set_label(lb)


def sanitize_strings(dic):
    """Do some sanitization for strings."""
    for k in dic:
        if isinstance(dic[k], str):
            dic[k].replace('{', '{{')
            dic[k].replace('}', '}}')


def get_world_coords(artist):
    """Get the world coordinates of an artist."""
    trans = artist.axes.transData.inverted()
    return trans.transform(artist.get_window_extent())


class AgrText:
    fmt = """string on
string loctype view
string {position}
string char size {size:.2f}
string color {color}
string def "{value}"
"""

    def get_position(self):
        trans = self.agr_axis.agr_figure.figure.transFigure.inverted()
        pos = trans.transform(self.text.get_window_extent())[0]
        pos = (pos + self.agr_figure.offset) * self.agr_figure.pagescale
        self.position = '{:.5f}, {:.5f}'.format(*pos)

    def __init__(self, text, agr_axis):
        self.text = text
        self.agr_axis = agr_axis
        self.agr_figure = agr_axis.agr_figure

        self.value = latex_to_xmgrace(text.get_text())
        self.size = text.get_fontsize() * self.agr_figure.fontscale
        self.color = AgrLine.color_index(text.get_color())
        self.get_position()
        sanitize_strings(self.__dict__)

    def __str__(self):
        return self.fmt.format(**self.__dict__)


class AgrLine:
    fmt = """hidden {hidden}
type {type}
legend "{label}"
line linestyle {linestyle}
line linewidth {linewidth}
line color {color}
symbol {marker}
symbol color {markeredgecolor}
symbol fill color {markerfacecolor}
symbol fill pattern {markerfill}
symbol linewidth {linewidth}
"""
    width_scale = 2
    cc = ColorConverter()
    linestyles = {'None': 0, '-': 1, ':': 2, '--': 3, '-.': 5}
    markers = defaultdict(
        lambda: 1,
        {'': 0, 'None': 0, 'o': 1, 's': 2, 'd': 3, '^': 4, '<': 5, 'v': 6, '>': 7, '+': 8, 'x': 9, '*': 10}
    )
    fillstyles = ('none', 'full', 'right', 'left', 'bottom', 'top')
    colors = ['white', 'black']

    def color_index(col):
        if col not in AgrLine.colors:
            AgrLine.colors.append(col)
        return AgrLine.colors.index(col)

    @property
    def data(self):
        o = '@type xy\n'
        for x, y in self.line.get_xydata():
            o += '{} {}\n'.format(x, y)
        o += '&'
        return o

    def get_label(self):
        lbl = self.line.get_label()
        self.label = latex_to_xmgrace(lbl) if not lbl.startswith('_line') else ''

    def get_linestyle(self):
        self.linestyle = self.linestyles[self.line.get_linestyle()]

    def get_linewidth(self):
        self.linewidth = self.line.get_linewidth() * self.width_scale

    def get_color(self):
        self.color = AgrLine.color_index(self.line.get_color())

    def get_marker(self):
        mk = self.line.get_marker()
        self.marker = self.markers[mk] if mk in self.markers else 1
        mfc = self.line.get_markerfacecolor()
        self.markerfacecolor = AgrLine.color_index(mfc)
        mec = self.line.get_markeredgecolor()
        self.markeredgecolor = AgrLine.color_index(mec)
        self.markeredgewidth = self.line.get_markeredgewidth() * self.width_scale
        self.markerfill = self.fillstyles.index(self.line.get_fillstyle())

    def __init__(self, line, agr_axis):
        self.agr_axis = agr_axis
        self.line = line
        self.hidden = 'false'
        self.type = 'xy'

        # run all get_ methods
        for d in dir(self):
            if d.startswith('get_'):
                getattr(self, d)()

        sanitize_strings(self.__dict__)

    def __str__(self):
        return self.fmt.format(**self.__dict__)


class AgrAxis:
    fmt = """world {world}
view {view}
title {title}
yaxes scale {yscale}
yaxis tick major {yticks}
xaxis label "{xlabel}"
xaxis label place {xlabelpos}
xaxis label char size {labelsize}
xaxis tick major {xticks}
xaxis ticklabel {xticklabel}
xaxis ticklabel place {xticklabelpos}
xaxis ticklabel char size {ticklabelsize}
xaxes scale {xscale}
yaxis label "{ylabel}"
yaxis label place {ylabelpos}
yaxis label char size {labelsize}
yaxis ticklabel {yticklabel}
yaxis ticklabel place {yticklabelpos}
yaxis ticklabel char size {ticklabelsize}
legend {legend}
legend loctype world
legend {legend_pos}
legend char size {legend_fontsize}
"""

    def get_world(self):
        xmin, xmax = self.axis.get_xlim()
        ymin, ymax = self.axis.get_ylim()
        self.world = '{:.3}, {:.3}, {:.3}, {:.3}'.format(xmin, ymin, xmax, ymax)
        box = self.axis.get_position()
        fx, fy = self.axis.figure.get_size_inches()
        sx, sy = self.agr_figure.pagescale
        offx, offy = self.agr_figure.offset
        self.view = '{:.3}, {:.3}, {:.3}, {:.3}'.format(
            (box.xmin + offx)*sx, (box.ymin + offy)*sy, 
            (box.xmax + offx)*sx, (box.ymax + offy)*sy
        )

    def get_title(self):
        self.title = latex_to_xmgrace(self.axis.get_title())

    def get_xyaxis(self):
        self.xlabel = latex_to_xmgrace(self.axis.get_xlabel())
        xpos = self.axis.xaxis.get_label_position()
        self.xlabelpos = 'normal' if xpos == 'bottom' else 'opposite'

        self.ylabel = latex_to_xmgrace(self.axis.get_ylabel())
        ypos = self.axis.yaxis.get_label_position()
        self.ylabelpos = 'normal' if ypos == 'left' else 'opposite'

        xsc = self.axis.get_xscale()
        self.xscale = 'Logarithmic' if 'log' in xsc else 'Normal'
        xticks = self.axis.get_xticks()
        if xsc == 'log':
            self.xticks = (xticks[1:] / xticks[:-1]).mean()
        else:
            self.xticks = (xticks[1:] - xticks[:-1]).mean()

        self.xticklabel = 'on' if any([x.get_visible() for x in self.axis.get_xticklabels()]) else 'off'
        xpos = self.axis.xaxis.get_ticks_position()
        if xpos == 'both':
            self.xticklabelpos = 'both'
        elif xpos == 'top':
            self.xticklabelpos = 'opposite'
        else:
            self.xticklabelpos = 'normal'

        xtlpos = set([x.get_position()[1] for x in self.axis.get_xticklabels() if x.get_visible()])
        if len(xtlpos) == 0:
            self.xticklabel = 'off'
            self.xticklabelpos = 'normal'
        elif len(xtlpos) == 1:
            self.xticklabel = 'on'
            self.xticklabelpos = 'opposite' if 1 in xtlpos else 'normal'
        else:
            self.xticklabel = 'on'
            self.xticklabelpos = 'both'

        ytlpos = set([x.get_position()[0] for x in self.axis.get_yticklabels() if x.get_visible()])
        if len(ytlpos) == 0:
            self.yticklabel = 'off'
            self.yticklabelpos = 'normal'
        elif len(ytlpos) == 1:
            self.yticklabel = 'on'
            self.yticklabelpos = 'opposite' if 1 in ytlpos else 'normal'
        else:
            self.yticklabel = 'on'
            self.yticklabelpos = 'both'

        ysc = self.axis.get_yscale()
        self.yscale = 'Logarithmic' if 'log' in ysc else 'Normal'
        yticks = self.axis.get_yticks()
        if ysc == 'log':
            self.yticks = (yticks[1:] / yticks[:-1]).mean()
        else:
            self.yticks = (yticks[1:] - yticks[:-1]).mean()

        self.labelsize = self.axis.xaxis.get_label().get_fontsize() * self.agr_figure.fontscale
        fs = self.axis.xaxis.get_ticklabels()[0].get_fontsize()
        self.ticklabelsize = fs * self.agr_figure.fontscale

    def get_legend(self):
        leg = self.axis.get_legend()
        if leg is None:
            self.legend = 'off'
            self.legend_pos = '0, 0'
            self.legend_fontsize = 0
        else:
            self.legend = 'on'
            for lbl, line in zip(leg.get_texts(), leg.get_lines()):
                pass
            pos = get_world_coords(leg)
            self.legend_pos = '{:.3f}, {:.3f}'.format(*pos.diagonal())
            self.legend_fontsize = leg.get_texts()[0].get_fontsize() * self.agr_figure.fontscale

    def __init__(self, axis, agr_fig):
        self.agr_figure = agr_fig
        self.axis = axis

        # run all get_ methods
        for d in dir(self):
            if d.startswith('get_'):
                getattr(self, d)()

        sanitize_strings(self.__dict__)
        self.lines = {'s{}'.format(i): AgrLine(l, self) for i, l in enumerate(axis.lines)}
        self.texts = [AgrText(t, self) for t in self.axis.texts]

    def __str__(self):
        o = self.fmt.format(**self.__dict__)
        for k, l in self.lines.items():
            o += textwrap.indent(str(l), prefix=k + ' ')
        for txt in self.texts:
            o += 'with string\n'
            o += textwrap.indent(str(txt), prefix='    ')
        return o


class AgrFigure:
    dpi = 96
    fontscale = 0.5
    fmt = """@version 50125
@page size {page}
"""
    data_fmt = "@target {target}\n{data}\n"""

    def collect_data(self):
        d = {}
        for ia, ax in self.axes.items():
            for il, ln in ax.lines.items():
                d['{}.{}'.format(ia.upper(), il.upper())] = ln.data
        return d

    def get_figprops(self):
        fx, fy = self.figure.get_size_inches()
        scx, scy = (1 + self.offset)
        # scy = (1 + self.offset_vertical)
        self.page = '{}, {}'.format(int(scx * self.dpi * fx), int(scy * self.dpi * fy))
        self.fontscale = AgrFigure.fontscale / min(fx * scx, fy * scy)

        self.pagescale = np.array([fx, fy]) / min(fx * scx, fy * scy)

    def __init__(self, figure, offset_horizontal=0, offset_vertical=0, convert_latex=True):
        tex2grace.do_latex_conversion = convert_latex
        self.figure = figure
        self.offset = np.array([offset_horizontal, offset_vertical])
        # make sure to draw the figure...
        canv = backend_agg.FigureCanvasAgg(figure)
        canv.draw()

        # run all get_ methods
        for d in dir(self):
            if d.startswith('get_'):
                getattr(self, d)()
        sanitize_strings(self.__dict__)

        self.axes = {'g{}'.format(i): AgrAxis(ax, self) for i, ax in enumerate(self.figure.axes)}

    def __str__(self):
        o = self.fmt.format(**self.__dict__)

        for i, col in enumerate(AgrLine.colors):
            # in matplotlib-1.5 to_rgb can not handle 'none', this was fixed in 2.0
            rgb = [int(x * 255) for x in AgrLine.cc.to_rgba(col)[:3]]
            o += '@map color {i} to ({rgb[0]}, {rgb[1]}, {rgb[2]}), "{col}"\n'.format(i=i, rgb=rgb, col=col)

        for k, ax in self.axes.items():
            o += textwrap.indent("on\nhidden false\ntype XY\nstacked false\n", prefix='@{} '.format(k))
            o += '@with {}\n'.format(k)
            o += textwrap.indent(str(ax), prefix='@    ')

        for k, d in self.collect_data().items():
            o += self.data_fmt.format(target=k, data=d)

        return o


def saveagr(fname, figure=None, offset_x=0, offset_y=0, convert_latex=True):
    """
    Save figure as xmgrace plot.

    If no figure is provided, this will save the current figure.

    Args:
        fname: Filename of the agr plot
        figure (opt.): Matplotlib figure to save, if None gcf() is used.
        offset_x, offset_y (opt.): Add an offest in x or y direction to the xmgrace plot.
        convert_latex (opt.): If latex strings will be converted to xmgrace.
    """
    if figure is None:
        figure = plt.gcf()
    with open(fname, 'w') as f:
        af = AgrFigure(figure, offset_horizontal=offset_x, offset_vertical=offset_y,
                       convert_latex=convert_latex)
        f.write(str(af))
