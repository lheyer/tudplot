
import altair
from altair import Config, Color, Shape, Column, Row, Encoding, Scale, Formula, Axis
from random import randint
import os
import logging

import matplotlib.pyplot as plt

from .tud import nominal_colors, full_colors


class BaseMixin(Encoding):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('scale', altair.Scale(zero=False))
        super().__init__(*args, **kwargs)


class LogMixin(BaseMixin):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('scale', altair.Scale(type='log'))
        super().__init__(*args, **kwargs)


class X(altair.X, BaseMixin):
    pass


class Y(altair.Y, BaseMixin):
    pass


class LogX(altair.X, LogMixin):
    pass


class LogY(altair.Y, LogMixin):
    pass


class DataHandler(altair.Data):

    def __init__(self, df):
        self._filename = '.altair.json'
        with open(self._filename, 'w') as f:
            f.write(df.to_json())
        super().__init__(url=self._filename)


class Chart(altair.Chart):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.configure_axis(subdivide=4)
        # self.configure(numberFormat='f')
        self.configure_scale(
            nominalColorRange=nominal_colors['b'],
            sequentialColorRange=nominal_colors['b'][:2],
            shapeRange=['circle', 'diamond', 'square', 'triangle-up', 'cross', 'triangle-down']
        )

    def encode(self, *args, color=None, **kwargs):
        if isinstance(color, str):
            if color.endswith(':F'):
                field = color[:-2]
                color = color.replace(':F', ':N')
                self.configure_scale(nominalColorRange=full_colors(len(set(self._data[field]))))

        for arg in args:
            if isinstance(arg, altair.X):
                kwargs['x'] = arg
            elif isinstance(arg, altair.Y):
                kwargs['y'] = arg
        return super().encode(color=color, **kwargs)

    def to_mpl(self):
        d = self.to_dict()
        fmt = 'o' if d.get('mark', 'point') is 'point' else '-'

        def encode(data, encoding, **kwargs):
            logging.debug(str(kwargs))
            if 'column' in encoding:
                channel = encoding.pop('column')
                ncols = len(data[channel.get('field')].unique())
                for col, (column, df) in enumerate(data.groupby(channel.get('field'))):
                    ax = plt.gca() if col > 0 else None
                    plt.subplot(kwargs.get('nrows', 1), ncols, col + 1, sharey=ax).set_title(column)
                    encode(df, encoding.copy(), secondary_column=col > 0, **kwargs.copy())
            elif 'color' in encoding:
                channel = encoding.pop('color')
                if channel.get('type') == 'quantitative':
                    colors = full_colors(len(data[channel.get('field')].unique()))
                else:
                    colors = nominal_colors['b']
                    while len(colors) < len(data[channel.get('field')].unique()):
                        colors *= 2
                for color, (column, df) in zip(colors, data.groupby(channel.get('field'))):
                    if 'label' in kwargs:
                        label = kwargs.pop('label') + ', {}'.format(column)
                    else:
                        label = str(column)
                    encode(df, encoding.copy(), color=color, label=label, **kwargs.copy())
            elif 'shape' in encoding:
                channel = encoding.pop('shape')
                markers = ['h', 'v', 'o', 's', '^', 'D', '<', '>']
                while len(markers) < len(data[channel.get('field')].unique()):
                    markers *= 2
                logging.debug(str(data[channel.get('field')].unique()))
                for marker, (column, df) in zip(markers, data.groupby(channel.get('field'))):
                    if 'label' in kwargs:
                        label = kwargs.pop('label') + ', {}'.format(column)
                    else:
                        label = str(column)
                    encode(df, encoding.copy(), marker=marker, label=label, **kwargs.copy())

            else:
                x_field = encoding.get('x').get('field')
                y_field = encoding.get('y').get('field')
                plt.xlabel(x_field)
                if not kwargs.pop('secondary_column', False):
                    plt.ylabel(y_field)
                else:
                    plt.tick_params(axis='y', which='both', labelleft='off', labelright='off')
                if 'scale' in encoding.get('x'):
                    plt.xscale(encoding['x']['scale'].get('type', 'linear'))
                if 'scale' in encoding.get('y'):
                    plt.yscale(encoding['y']['scale'].get('type', 'linear'))
                plt.plot(data[x_field], data[y_field], fmt, **kwargs)
                plt.legend(loc='best', fontsize='small')

        encode(self._data, d.get('encoding'))
        plt.tight_layout(pad=0.5)


class Arrhenius(Chart):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.transform_data(calculate=[Formula(field='1000K/T', expr='1000/datum.T')])
        self.data['1000 K / T'] = 1000 / self.data['T']
        self.encode(x=X('1000 K / T'))
