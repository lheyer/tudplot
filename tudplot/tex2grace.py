
from collections import OrderedDict
import logging
import re

patterns = OrderedDict()
patterns['\$'] = ''
patterns['¹'] = r'\S1\N'
patterns['²'] = r'\S2\N'
patterns['³'] = r'\S3\N'
patterns['⁴'] = r'\S4\N'
patterns['⁵'] = r'\S5\N'
patterns['⁶'] = r'\S6\N'
patterns['⁷'] = r'\S7\N'
patterns['⁸'] = r'\S8\N'
patterns['⁹'] = r'\S9\N'
patterns['⁻'] = r'\S-\N'
patterns[r'\\,'] = r'\-\- \+\+'
patterns[r'\\[;:.]'] = ''
patterns[r'\\math(?:tt|sf|it|rm)({[^}]+})'] = r'\1'
patterns[r'\^({[^}]+}|.)'] = r'\S\1\N'
patterns[r'\_({[^}]+}|.)'] = r'\s\1\N'
# Remove any left over latex groups as the last step
patterns[r'[{}]'] = ''

# Greek letters in xmgrace are written by switching to symbol-font:
# "\x a\f{}" will print an alpha and switch back to normal font
greek = {
    'alpha': 'a', 'beta': 'b', 'gamma': 'g', 'delta': 'd', 'epsilon': 'e', 'zeta': 'z',
    'eta': 'h', 'theta': 'q', 'iota': 'i', 'kappa': 'k', 'lambda': 'l', 'mu': 'm',
    'nu': 'n', 'xi': 'x', 'omicron': 'o', 'pi': 'p', 'rho': 'r', 'sigma': 's',
    'tau': 't', 'upsilon': 'u', 'phi': 'f', 'chi': 'c', 'psi': 'y', 'omega': 'w',
    'varphi': 'j', 'varepsilon': 'e', 'vartheta': 'J', 'varrho': 'r',
    'Phi': 'F',
    'langle': r'\#{{e1}}', 'rangle': r'\#{{f1}}', 'infty': r'\c%\C', 'cdot': r'\#{{d7}}',
    'sqrt': r'\#{{d6}}', 'propto': r'\#{{b5}}',
}
for latex, xmg in greek.items():
    patt = r'\\{}'.format(latex)
    repl = r'\\x {}\\f{{{{}}}}'.format(xmg)
    patterns[patt] = repl


def latex_to_xmgrace(string):
    logging.debug('Convert to xmgrace: {}'.format(string))
    for patt, repl in patterns.items():
        string = re.sub(patt, repl, string)
    logging.debug('To -> {}'.format(string))
    return string
