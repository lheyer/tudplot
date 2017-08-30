from __future__ import print_function
import re

small_greek = {'alpha': u'\u03b1',
               'beta': u'\u03b2',
               'gamma': u'\u03b3',
               'delta': u'\u03b4',
               'epsilon': u'\u03b5',
               'zeta': u'\u03b6',
               'eta': u'\u03b7',
               'theta': u'\u03b8',
               'iota': u'\u03b9',
               'kappa': u'\u03ba',
               'lambda': u'\u03bb',
               'mu': u'\u03bc',
               'nu': u'\u03bd',
               'xi': u'\u03be',
               'omicron': u'\u03bf',
               'pi': u'\u03c0',
               'rho': u'\u03c1',
               'varsigma': u'\u03c2',
               'sigma': u'\u03c3',
               'tau': u'\u03c4',
               'ypsilon': u'\u03c5',
               'phi': u'\u03c6',
               'chi': u'\u03c7',
               'psi': u'\u03c8',
               'omega': u'\u03c9'
               }

big_greek = {'Alpha': u'\u0391',
             'Beta': u'\u0392',
             'Gamma': u'\u0393',
             'Delta': u'\u0394',
             'Epsilon': u'\u0395',
             'Zeta': u'\u0396',
             'Eta': u'\u0397',
             'Theta': u'\u0398',
             'Iota': u'\u0399',
             'Kappa': u'\u039a',
             'Lambda': u'\u039b',
             'Mu': u'\u039c',
             'Nu': u'\u039d',
             'Xi': u'\u039e',
             'Omicron': u'\u039f',
             'Pi': u'\u03a0',
             'Rho': u'\u03a1',
             'Varsigma': u'\u03a2',
             'Sigma': u'\u03a3',
             'Tau': u'\u03a4',
             'Ypsilon': u'\u03a5',
             'Phi': u'\u03a6',
             'Chi': u'\u03a7',
             'Psi': u'\u03a8',
             'Omega': u'\u03a9'
             }

special_chars = {'infty': u'\u221e',
                 'int': u'\u222b',
                 'perp': u'\u27c2',
                 'para': u'\u2225',
                 'leftarrow': u'\u21d0',
                 'rightarrow': u'\u21d2',
                 'leftrightarrow': u'\u21d4',
                 '\n': '<br>',
                 '*': u'\u00b7',
                 'plmin': u'\u00b1'}

small_greek_grace = {'alpha': r'\f{Symbol}a\f{}',
                     'beta': r'\f{Symbol}b\f{}',
                     'gamma': r'\f{Symbol}g\f{}',
                     'delta': r'\f{Symbol}d\f{}',
                     'epsilon': r'\f{Symbol}e\f{}',
                     'zeta': r'\f{Symbol}z\f{}',
                     'eta': r'\f{Symbol}h\f{}',
                     'theta': r'\f{Symbol}q\f{}',
                     'iota': r'\f{Symbol}i\f{}',
                     'kappa': r'\f{Symbol}k\f{}',
                     'lambda': r'\f{Symbol}l\f{}',
                     'mu': r'\f{Symbol}m\f{}',
                     'nu': r'\f{Symbol}n\f{}',
                     'xi': r'\f{Symbol}x\f{}',
                     'omicron': r'\f{Symbol}o\f{}',
                     'pi': r'\f{Symbol}p\f{}',
                     'rho': r'\f{Symbol}r\f{}',
                     'sigma': r'\f{Symbol}s\f{}',
                     'tau': r'\f{Symbol}t\f{}',
                     'ypsilon': r'\f{Symbol}u\f{}',
                     'phi': r'\f{Symbol}f\f{}',
                     'chi': r'\f{Symbol}c\f{}',
                     'psi': r'\f{Symbol}y\f{}',
                     'omega': r'\f{Symbol}w\f{}'
               }

big_greek_grace = {'Alpha': r'\f{Symbol}A\f{}',
                   'Beta': r'\f{Symbol}B\f{}',
                   'Gamma': r'\f{Symbol}g\f{}',
                   'Delta': r'\f{Symbol}D\f{}',
                   'Epsilon': r'\f{Symbol}E\f{}',
                   'Zeta': r'\f{Symbol}Z\f{}',
                   'Eta': r'\f{Symbol}H\f{}',
                   'Theta': r'\f{Symbol}Q\f{}',
                   'Iota': r'\f{Symbol}I\f{}',
                   'Kappa': r'\f{Symbol}K\f{}',
                   'Lambda': r'\f{Symbol}L\f{}',
                   'Mu': r'\f{Symbol}M\f{}',
                   'Nu': r'\f{Symbol}N\f{}',
                   'Xi': r'\f{Symbol}X\f{}',
                   'Omicron': r'\f{Symbol}O\f{}',
                   'Pi': r'\f{Symbol}P\f{}',
                   'Rho': r'\f{Symbol}R\f{}',
                   'Sigma': r'\f{Symbol}S\f{}',
                   'Tau': r'\f{Symbol}T\f{}',
                   'Ypsilon': r'\f{Symbol}U\f{}',
                   'Phi': r'\f{Symbol}F\f{}',
                   'Chi': r'\f{Symbol}C\f{}',
                   'Psi': r'\f{Symbol}U\f{}',
                   'Omega': r'\f{Symbol}Q\f{}'
                   }

special_chars_grace = {'infty': r'\f{Symbol}\c%\f{}'}


full_chars = dict()
for d in [big_greek, small_greek, special_chars]:
    full_chars.update(d)

full_char_reverse = {y: x for x, y in full_chars.items()}


def _replace_unicode(text):
    for k, v in full_chars.items():
        text = text.replace(k, v)
    return text


def _replacesub(text):
    sub_pattern_1 = re.compile('(_\{\S*?\})')
    sub_pattern_2 = re.compile('_\S')
    for s in sub_pattern_1.findall(text):
        text = text.replace(s, u'<sub>{0:}</sub>'.format(s[2:-1]))
    for s in sub_pattern_2.findall(text):
        text = text.replace(s, u'<sub>{0:}</sub>'.format(s[1:]))
    return text


def _replacesup(text):
    sup_pattern_1 = re.compile('\^\{\S*?\}')
    sup_pattern_2 = re.compile('\^\S')
    for s in sup_pattern_1.findall(text):
        text = text.replace(s, u'<sup>{0:}</sup>'.format(s.strip()[2:-1]))
    for s in sup_pattern_2.findall(text):
        text = text.replace(s, u'<sup>{0:}</sup>'.format(s.strip()[1:]))
    return text


def str2format(text):
    text = _replacesub(text)
    text = _replacesup(text)
    text = _replace_unicode(text)

    return text


def format2str(text):
    for k, v in full_char_reverse.items():
        text = text.replace(k, v)
    for k, v in [('<sub>', '_{'), ('</sub>', '}'), ('<sup>', '^{'), ('</sup>', '}')]:
        text = text.replace(k, v)

    return text


def format2grace(text):
    text = format2str(text)
    for k, v in [('_{', r'\s'), ('}', r'\N'), ('^{', r'\S'), ('}', r'\N')]:
        text = text.replace(k, v)
    for k, v in big_greek_grace.items():
        text = text.replace(k, v)
    for k, v in small_greek_grace.items():
        text = text.replace(k, v)
    for k, v in special_chars_grace.items():
        text = text.replace(k, v)

    return text


def grace2str(text):
    text = text.replace(r'\s', '_{').replace('\S', '^{')
    text = text.replace(r'\N', '}')
    text = text.replace(r'\f{}', '')

    return text

if __name__ == '__main__':
    stringtext = 'M_{infty}[1-alpha exp(-x/T_{1,1})^{beta_1}]'
    print('Input:\t{}'.format(stringtext))
    print(u'Output:\t{}'.format(str2format(stringtext)))
    print('Input 2:\t{}'.format(format2str(str2format(stringtext))))
    print('Grace:\t{}'.format(format2grace(str2format(stringtext))))
    print(u'Output 2:\t{}'.format(str2format(format2str(str2format(stringtext)))))
