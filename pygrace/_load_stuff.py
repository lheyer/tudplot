from __future__ import print_function
import os.path
import os
import imp
import sys
import configparser as ConfigParser

if os.name == 'nt':
    path_to_log = os.path.expanduser('~\.auswerten')
else:
    path_to_log = os.path.expanduser('~/.auswerten')
path_to_module = os.path.dirname(os.path.abspath(__file__))


def reload_(filename):
    (path, name) = os.path.split(filename)
    (name, ext) = os.path.splitext(name)

    try:
        file, filename, data = imp.find_module(name, [path])
    except ImportError:
        print('No module {} found'.format(name))
    try:
        mod = imp.load_module(name, file, filename, data)
        return mod
    except UnboundLocalError:
        pass
    if file:
        file.close()


def import_(filename):
    """
    Tries to add random file to sys.modules. Insecure as fuck and predestined to break something
    (it will overload other modules)
    """
    (path, name) = os.path.split(filename)
    (name, ext) = os.path.splitext(name)
    try:
        return sys.modules[name]
    except KeyError:
        pass
    try:
        file, filename, data = imp.find_module(name, [path])
    except ImportError:
        print('No module {} found'.format(name))
    try:
        mod = imp.load_module(name, file, filename, data)
        return mod
    except UnboundLocalError:
        pass
    finally:
        # Since we may exit via an exception, close fp explicitly.
        try:
            if file:
                file.close()
        except UnboundLocalError:
            if not os.path.exists(path):
                os.makedirs(path)
            from shutil import copyfile
            if os.name == 'nt':
               copyfile(os.path.join(path_to_module, 'models\myfitmodels.py'), filename)
            else:
                copyfile(os.path.join(path_to_module, './models/myfitmodels.py'), filename)
            # open(filename, 'a').close()

user_model_path = os.path.join(path_to_log, 'myfitmodels.py')
userfitmodels = import_(user_model_path)


def read_grace_conf(mode):
    __path_to_config = os.path.join(path_to_log, 'grace.conf')
    config = ConfigParser.SafeConfigParser()
    config.read(__path_to_config)

    if config.has_section(mode):
        width = config.getfloat(mode, 'width')
        height = config.getfloat(mode, 'height')
        bottom_m = config.getfloat(mode, 'bottom margin')
        left_m = config.getfloat(mode, 'left margin')
        top_m = config.getfloat(mode, 'top margin')
        right_m = config.getfloat(mode, 'right margin')
        title = config.getint(mode, 'title')
        haxis_t = config.getint(mode, 'hor axis tick')
        vaxis_t = config.getint(mode, 'ver axis tick')
        haxis_l = config.getint(mode, 'hor axis label')
        vaxis_l = config.getint(mode, 'ver axis label')
        leg = config.getint(mode, 'legend')
    else:
        width = round(11 * 2.54, 2)
        height = round(8.5 * 2.54, 2)
        bottom_m = round(0.15 * 8.5 * 2.54, 2)
        left_m = round(0.15 * 8.5 * 2.54, 2)
        top_m = round(0.15 * 8.5 * 2.54, 2)
        right_m = round((11 / 8.5 - 1.15) * 8.5 * 2.54, 2)
        haxis_l = 100
        haxis_t = 100
        vaxis_l = 100
        vaxis_t = 100
        leg = 100
        title = 100
    if config.has_section('sizes'):
        sym = config.getfloat('sizes', 'symbol')
        line = config.getfloat('sizes', 'line')
        f_line = config.getfloat('sizes', 'fit_line')
    else:
        sym = 10
        line = 1
        f_line = 1

    return (width, height), (bottom_m, top_m, left_m, right_m), \
           ((haxis_t, haxis_l), (vaxis_t, vaxis_l), title, leg), \
           (sym, line, f_line)

