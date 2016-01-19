from matplotlib.colors import ColorConverter
from matplotlib.cbook import is_string_like
import re


def indexed(list, default=None):
    def index(arg):
        if arg in list:
            return list.index(arg)
        else:
            return default
    return index

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
    #'legend': {'type': 'static', 'fmt': 'legend on'},
    'title': {'type': 'value', 'fmt': 'title "{value}"'},
    'xlabel': {'type': 'value', 'fmt': 'xaxis label "{value}"'},
    'ylabel': {'type': 'value', 'fmt': 'yaxis label "{value}"'},
    'xscale': {'type': 'value', 'fmt': 'xaxes scale Logarithmic',
               'condition': lambda scale: scale is 'log'},
    'yscale': {'type': 'value', 'fmt': 'yaxes scale Logarithmic',
               'condition': lambda scale: scale is 'log'},

}

xmgrace_mapping = {
    'line': {
        'get_linewidth': {'fmt': '    {} line linewidth {}'}
    }
}


class AgrFile:
    head = body = tail = ''
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
        rgb_tuple = tuple(int(255 * c) for c in cc.to_rgba_array(color)[0, :3])
        agr.writeline('map color {index} to {rgb}, "{color}"',
                      part='head', index=i, rgb=rgb_tuple, color=color)

    agr.save(filename)
