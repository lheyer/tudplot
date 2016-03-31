
import re

from matplotlib.colors import ColorConverter
from matplotlib.cbook import is_string_like
import numpy as np


def indexed(list, default=None):
    def index(arg):
        if arg in list:
            return list.index(arg)
        else:
            return default
    return index


def get_world(line):
    xmin, xmax = line.get_xlim()
    ymin, ymax = line.get_ylim()
    return '{}, {}, {}, {}'.format(xmin, ymin, xmax, ymax)


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


# dict of line attributes:
# value describes the type of the attribute:
#     static : a static entry
#     value : use value
#     index : use index of value in list
#     map:    add value to list if necessary
agr_line_attrs = {
    'hidden': {'type': 'static', 'fmt': 'hidden false'},
    'type': {'type': 'static', 'fmt': 'type xy'},
    'label': {'type': 'value', 'fmt': 'legend "{value}"',
              'condition': lambda lbl: re.search('_line\d+', lbl) is None},
    'linestyle': {'type': 'index', 'fmt': 'line {attr} {value}'},
    'linewidth': {'type': 'value', 'fmt': 'line {attr} {value}'},
    'color': {'type': 'index map', 'fmt': 'line {attr} {value}'},
    'marker': {'type': 'index', 'fmt': 'symbol {value}'},
    'markerfacecolor': {'type': 'index map', 'maplist': 'color', 'fmt': 'symbol color {value}'}
}
agr_axis_attrs = {
    'world': {'type': 'function', 'function': get_world, 'fmt': 'world {value}'},
    'title': {'type': 'value', 'fmt': 'title "{value}"'},
    'xlabel': {'type': 'value', 'fmt': 'xaxis label "{value}"'},
    'ylabel': {'type': 'value', 'fmt': 'yaxis label "{value}"'},
    'xscale': {'type': 'value', 'fmt': 'xaxes scale Logarithmic',
               'condition': lambda scale: scale is 'log'},
    'yscale': {'type': 'value', 'fmt': 'yaxes scale Logarithmic',
               'condition': lambda scale: scale is 'log'},
    'xticks': {'type': 'function', 'fmt': 'xaxis tick major {value}',
               'function': get_major_ticks('x')},
    'yticks': {'type': 'function', 'fmt': 'yaxis tick major {value}',
               'function': get_major_ticks('y')},

}

xmgrace_mapping = {
    'line': {
        'get_linewidth': {'fmt': '    {} line linewidth {}'}
    }
}


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

patterns = {
    '\$': '',
    r'\^({.+}|.)': r'\S\1\N',
    r'\_({.+}|.)': r'\s\1\N',
}

# Greek letters in xmgrace are written by switching to symbol-font:
# "\x a\f{}" will print an alpha an switch back to normal font
greek = {
    'alpha': 'a', 'beta': 'b', 'gamma': 'g', 'delta': 'd', 'epsilon': 'e', 'zeta': 'z',
    'eta': 'h', 'theta': 'q', 'iota': 'i', 'kappa': 'k',  'lambda': 'l',  'mu': 'm',
    'nu': 'n', 'xi': 'x', 'omicron': 'o', 'pi': 'p', 'rho': 'r', 'sigma': 's',
    'tau': 't', 'upsilon': 'u', 'phi': 'f', 'chi': 'c', 'psi': 'y', 'omega': 'w',
    'varphi': 'j', 'varepsilon': 'e', 'vartheta': 'J', 'varrho': 'r'
}
for latex, xmg in greek.items():
    patt = r'\\{}'.format(latex)
    repl = r'\\x {}\\f{{}}'.format(xmg)
    patterns[patt] = repl


def latex_to_xmgrace(string):

    for patt, repl in patterns.items():
        string = re.sub(patt, repl, string)

    return string


def process_attributes(attrs, source, agr, prefix=''):
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


def export_to_agr(figure, filename):
    """
    Export a matplotlib figure to xmgrace format.
    """
    cc = ColorConverter()
    agr = AgrFile()
    agr_attr_lists['color'] = ['white', 'black']
    # agr_colors =

    for i, axis in enumerate(figure.axes):

        agr_axis = 'g{}'.format(i)

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

    agr.indent = 0
    for i, color in enumerate(agr_attr_lists['color']):
        if color is not 'none':
            rgb_tuple = tuple(int(255 * c) for c in cc.to_rgba_array(color)[0, :3])
            agr.writeline('map color {index} to {rgb}, "{color}"',
                          part='head', index=i, rgb=rgb_tuple, color=color)

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
                ma = re.search('([sS]\d) .+ "(.*)"', org_line)
                if ma is not None:
                    cur_graph[ma.group(1).lower()] = {'label': ma.group(2)}
            elif '@target' in line:
                ma = re.search('(g\d)\.(s\d)', line.lower())
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
