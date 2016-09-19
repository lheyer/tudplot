
import re
from collections import OrderedDict

from matplotlib.colors import ColorConverter
from matplotlib.cbook import is_string_like
import numpy as np

from .tud import tudcolors


patterns = OrderedDict()
patterns['\$'] = ''
patterns[r'\\mathtt{(.+)}'] = r'\1'
patterns[r'\^({.+}|.)'] = r'\S\1\N'
patterns[r'\_({.+}|.)'] = r'\s\1\N'

# Greek letters in xmgrace are written by switching to symbol-font:
# "\x a\f{}" will print an alpha and switch back to normal font
greek = {
    'alpha': 'a', 'beta': 'b', 'gamma': 'g', 'delta': 'd', 'epsilon': 'e', 'zeta': 'z',
    'eta': 'h', 'theta': 'q', 'iota': 'i', 'kappa': 'k',  'lambda': 'l',  'mu': 'm',
    'nu': 'n', 'xi': 'x', 'omicron': 'o', 'pi': 'p', 'rho': 'r', 'sigma': 's',
    'tau': 't', 'upsilon': 'u', 'phi': 'f', 'chi': 'c', 'psi': 'y', 'omega': 'w',
    'varphi': 'j', 'varepsilon': 'e', 'vartheta': 'J', 'varrho': 'r'
}
for latex, xmg in greek.items():
    patt = r'\\{}'.format(latex)
    repl = r'\\x {}\\f{{{{}}}}'.format(xmg)
    patterns[patt] = repl


def latex_to_xmgrace(string):

    for patt, repl in patterns.items():
        string = re.sub(patt, repl, string)
    return string


def indexed(list, default=None):
    def index(arg):
        if arg in list:
            return list.index(arg)
        else:
            return default
    return index


def get_viewport_coords(artist):
    """
    Get the viewport coordinates of an artist.
    """
    trans = artist.axes.transAxes.inverted()
    return trans.transform(artist.get_window_extent())


def get_world_coords(artist):
    """
    Get the world coordinates of an artist.
    """
    trans = artist.axes.transData.inverted()
    return trans.transform(artist.get_window_extent())


def get_world(axis):
    xmin, xmax = axis.get_xlim()
    ymin, ymax = axis.get_ylim()
    return '{}, {}, {}, {}'.format(xmin, ymin, xmax, ymax)


def get_view(axis):
    box = axis.get_position()
    fx, fy = axis.figure.get_size_inches()
    sx = fx / min(fx, fy)
    sy = fy / min(fx, fy)
    return '{:.3}, {:.3}, {:.3}, {:.3}'.format(box.xmin*sx, box.ymin*sy, box.xmax*sx, box.ymax*sy)


def get_major_ticks(dim):
    def get_major_dticks(axis):
        ticks = getattr(axis, 'get_{}ticks'.format(dim))()
        scale = getattr(axis, 'get_{}scale'.format(dim))()
        if scale is 'log':
            value = (ticks[1:] / ticks[:-1]).mean()
        else:
            value = (ticks[1:] - ticks[:-1]).mean()

        return value

    return get_major_dticks
agr_attr_lists = {
    # Linestyles in xmgrace: None are styles that are by default
    # not defined in matplotlib (longer dashes and double dots)
    # First entry should always be None, since index starts at 1
    'linestyle': ['None', '-', ':', '--', None, '-.', None, None, None],
    'marker': ['None', 'o', 's', 'd', '^', '<', 'v', '>', '+', 'x', '*']
}


def get_legend(axis):
    if axis.get_legend() is not None:
        return 'on'
    else:
        return 'off'


def get_legend_position(axis):
    return '{}, {}'.format(*get_world_coords(axis.get_legend())[[(0, 1), (0, 1)]])


def get_text_position(text):
    return '{}, {}'.format(*get_world_coords(text)[0])


class StaticAttribute:
    """
    A static attribute that just writes a line to the agr file if it is set.
    Functions also as a base class for other attribute classes.
    """

    def __init__(self, key, fmt):
        """
        Args:
            key: The name of the attribute.
            fmt: The string which is written to the agr file.
        """
        self.key = key
        self.fmt = fmt

    def format(self, source=None):
        """
        Return the (formatted) string of the attribute.

        Args:
            source: The python object, which is only included here for signature reasons
        """
        return self.fmt


class ValueAttribute(StaticAttribute):
    """
    An attribute which writes a key value pair into the agr file.
    The agr string has the format: '{fmt} {value}'
    """
    attr_lists = {
        'linestyle': ('None', '-', ':', '--', None, '-.', None, None, None),
        'marker': ('None', 'o', 's', 'd', '^', '<', 'v', '>', '+', 'x', '*'),
        'color': ['white', 'black'],
    }

    def _get_value(self, source):
        value = getattr(source, 'get_{}'.format(self.key))()
        if is_string_like(value):
            value = latex_to_xmgrace(value)
            if not self.index:
                value = '"{}"'.format(value)

        return value

    def __init__(self, *args, index=None, function=None, condition=None):
        """
        Args:
            *args: Arguments of super().__init__()
            index:
                True if value should be mapped to an index. If this is a str this will
                be used as the index lists key.
            function: A function that is used to fetch the value from the source.
            condition: A function that decides if the attribute is written to the agr file.
        """
        super().__init__(*args)

        if index:
            if index is True:
                self.index = self.key
            else:
                self.index = index
            self.attr_lists.setdefault(self.index, [])
        else:
            self.index = False

        if function is not None:
            self._get_value = function
        self.condition = condition or (lambda x: True)

    def format(self, source):
        value = self._get_value(source)
        if not self.condition(value):
            return None
        if self.index:
            attr_list = self.attr_lists[self.index]
            index = indexed(attr_list)(value)
            if index is None:
                try:
                    attr_list.append(value)
                    index = attr_list.index(value)
                except AttributeError:
                    print('index not found:', value, index, attr_list)
                    index = 1
            value = index
        return ' '.join([self.fmt, str(value)])

agr_line_attrs = [
    StaticAttribute('hidden', 'hidden false'),
    StaticAttribute('type', 'type xy'),
    ValueAttribute('label', 'legend', condition=lambda lbl: re.search(r'\\sl\\Nine\d+', lbl) is None),
    ValueAttribute('linestyle', 'line linestyle', index=True),
    ValueAttribute('linewidth', 'line linewidth'),
    ValueAttribute('color', 'line color', index=True),
    ValueAttribute('marker', 'symbol', index=True),
    ValueAttribute('markeredgecolor', 'symbol color', index='color'),
    ValueAttribute('markerfacecolor', 'symbol fill color', index='color'),
    ValueAttribute('markeredgewidth', 'symbol linewidth'),
]

agr_axis_attrs = [
    ValueAttribute('world', 'world', function=get_world),
    ValueAttribute('view', 'view', function=get_view),
    ValueAttribute('title', 'title'),
    ValueAttribute('xlabel', 'xaxis label'),
    ValueAttribute('ylabel', 'yaxis label'),
    ValueAttribute('xscale', 'xaxes scale Logarithmic', condition=lambda scale: 'log' in scale),
    ValueAttribute('yscale', 'yaxes scale Logarithmic', condition=lambda scale: 'log' in scale),
    ValueAttribute('xticks', 'xaxis tick major', function=get_major_ticks('x')),
    ValueAttribute('yticks', 'yaxis tick major', function=get_major_ticks('y')),
    ValueAttribute('legend', 'legend', function=get_legend),
    StaticAttribute('legend', 'legend loctype world'),
    ValueAttribute('legend', 'legend', function=get_legend_position)
]

agr_text_attrs = [
    StaticAttribute('string', 'on'),
    StaticAttribute('string', 'loctype world'),
    ValueAttribute('position', '', function=get_text_position),
    ValueAttribute('text', 'def')
]


class AgrFile:
    head = '@version 50125\n'
    body = tail = ''
    indent = 0
    kwargs = {}

    def writeline(self, text, part='body', **kwargs):
        self.kwargs = {**self.kwargs, **kwargs}
        content = getattr(self, part)
        content += '@' + ' ' * self.indent + text.format(**self.kwargs) + '\n'
        setattr(self, part, content)

    def writedata(self, data):
        self.tail += '@target {axis}.{line}\n@type xy\n'.format(**self.kwargs)
        for x, y in data:
            self.tail += '{} {}\n'.format(x, y)
        self.tail += '&\n'

    def save(self, filename):
        with open(filename, 'w') as file:
            file.write(self.head)
            file.write(self.body)
            file.write(self.tail)


def _process_attributes(attrs, source, agr, prefix=''):
    for attr, attr_dict in attrs.items():
        attr_type = attr_dict['type']
        if 'static' in attr_type:
            value = ''
        elif 'function' in attr_type:
            value = attr_dict['function'](source)
        else:
            value = getattr(source, 'get_{}'.format(attr))()
            if 'condition' in attr_dict:
                if not attr_dict['condition'](value):
                    continue
            if is_string_like(value):
                value = latex_to_xmgrace(value)
            if 'index' in attr_type:
                attr_list = agr_attr_lists[attr_dict.get('maplist', attr)]
                index = indexed(attr_list)(value)
                if index is None:
                    if 'map' in attr_type:
                        attr_list.append(value)
                        index = attr_list.index(value)
                    else:
                        index = 1
                value = index

        agr.writeline(prefix + attr_dict['fmt'], attr=attr, value=value)


def process_attributes(attrs, source, agr, prefix=''):
    for attr in attrs:
        fmt = attr.format(source)
        if fmt is not None:
            agr.writeline(prefix + fmt)


def export_to_agr(figure, filename):
    """
    Export a matplotlib figure to xmgrace format.
    """
    cc = ColorConverter()
    agr = AgrFile()
    # agr_attr_lists['color'] = ['white', 'black']
    # agr_colors =
    papersize = figure.get_size_inches()*150
    agr.writeline('page size {}, {}'.format(*papersize))
    for i, axis in enumerate(figure.axes):

        agr_axis = 'g{}'.format(i)
        agr.indent = 0
        agr.writeline('{axis} on', axis=agr_axis)
        agr.writeline('{axis} hidden false')
        agr.writeline('{axis} type XY')
        agr.writeline('{axis} stacked false')
        agr.writeline('with {axis}')
        agr.indent = 4

        process_attributes(agr_axis_attrs, axis, agr)

        for j, line in enumerate(axis.lines):
            agr.kwargs['line'] = 's{}'.format(j)
            process_attributes(agr_line_attrs, line, agr, '{line} ')
            agr.writedata(line.get_xydata())

        for text in axis.texts:
            agr.indent = 0
            agr.writeline('with string')
            agr.indent = 4
            process_attributes(agr_text_attrs, text, agr, 'string ')

    agr.indent = 0
    tudcol_rev = {}
    for style, colors in tudcolors.items():
        for i, col in enumerate(colors):
            rgba, = cc.to_rgba_array(col)
            tudcol_rev[tuple(rgba)] = 'tud{}{}'.format(i, style)

    for i, color in enumerate(ValueAttribute.attr_lists['color']):
        # print(i, color)
        if color is not 'none':
            rgba, = cc.to_rgba_array(color)
            rgb_tuple = tuple(int(255 * c) for c in rgba[:3])
            color_name = tudcol_rev.get(tuple(rgba), color)
            agr.writeline('map color {index} to {rgb}, "{color}"',
                          part='head', index=i, rgb=rgb_tuple, color=color_name)

    agr.save(filename)


def load_agr_data(agrfile):
    """
    Load all named data sets from an agrfile.
    """
    graphs = {}
    cur_graph = None
    target = None
    with open(agrfile, 'r') as f:
        for org_line in f.readlines():
            line = org_line.lower()
            if '@with' in line:
                graph_id = line.split()[1]
                if graph_id not in graphs:
                    graphs[graph_id] = {}
                cur_graph = graphs[graph_id]
            elif 'legend' in line and cur_graph is not None:
                ma = re.search('([sS]\d+) .+ "(.*)"', org_line)
                if ma is not None:
                    cur_graph[ma.group(1).lower()] = {'label': ma.group(2)}
            elif '@target' in line:
                ma = re.search('(g\d+)\.(s\d+)', line.lower())
                gid = ma.group(1)
                sid = ma.group(2)
                target = []
                if sid not in graphs[gid]:
                    print('Target {}.{} has no label.'.format(gid, sid))
                    continue
                graphs[gid][sid]['data'] = target
            elif target is not None and '@type' in line:
                continue
            elif '&' in line:
                target = None
            elif target is not None:
                target.append([float(d) for d in line.split()])

    data = {}
    for _, graph in graphs.items():
        for _, set in graph.items():
            if 'data' in set:
                data[set['label']] = np.array(set['data'])
            else:
                print(_, set)
                data[set['label']] = np.empty((0,))

    return data
