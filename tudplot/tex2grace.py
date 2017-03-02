
from collections import OrderedDict
import logging
import re

patterns = OrderedDict()
patterns['\$'] = ''
patterns[r'\\math(?:tt|sf|it)({.+})'] = r'\1'
patterns[r'\^({.+}|.)'] = r'\s\1\N'
patterns[r'\_({.+}|.)'] = r'\s\1\N'
# Remove any left over latex groups as the last step
patterns[r'[{}]'] = ''

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
    logging.debug('Convert to xmgrace: {}'.format(string))
    for patt, repl in patterns.items():
        string = re.sub(patt, repl, string)
    logging.debug('To -> {}'.format(string))
    return string
