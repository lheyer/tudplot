import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import Iterable
from matplotlib.cbook import flatten
from itertools import cycle


def facet_plot(dframe, facets, props, ydata, layout=None, newfig=True, figsize=None,
               legend=True, individual_legends=False, hide_additional_axes=True, zorder='default', **kwargs):
    if newfig:
        nr_facets = len(dframe.groupby(facets))
        if layout is None:
            for i in range(2, nr_facets // 2):
                if nr_facets % i == 0:
                    layout = (nr_facets // i, i)
                    break
            if layout is None:
                n = int(np.ceil(nr_facets / 2))
                layout = (n, 2)
        fig, axs = plt.subplots(
            nrows=layout[0],
            ncols=layout[1],
            sharex=True, sharey=True, figsize=figsize
        )
        if hide_additional_axes:
            for ax in fig.axes[nr_facets:]:
                ax.set_axis_off()
    else:
        fig = plt.gcf()
        axs = fig.axes

    cycl = cycle(plt.rcParams['axes.prop_cycle'])
    prop_styles = {ps: next(cycl) for ps, _ in dframe.groupby(props)}

    if zorder is 'default':
        dz = 1
        zorder = 0
    elif zorder is 'reverse':
        dz = -1
        zorder = 0
    else:
        dz = 0

    if legend:
        ax0 = fig.add_subplot(111, frame_on=False, zorder=-9999)
        ax0.set_axis_off()
        plot_kwargs = kwargs.copy()
        for k in ['logx', 'logy', 'loglog']:
            plot_kwargs.pop(k, None)
        for l, p in prop_styles.items():
            ax0.plot([], label=str(l), **p, **plot_kwargs)
        ax0.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='x-small')
    for ax, (ps, df) in zip(flatten(axs), dframe.groupby(facets, squeeze=False)):
        for prop, df_prop in df.groupby(props):
            df_prop[ydata].plot(ax=ax, label=str(prop), zorder=zorder, **prop_styles[prop], **kwargs)
            zorder += dz
        #  ax.title(0.5, 0.1, '{},{}'.format(*ps), transform=ax.transAxes, fontsize='small')

        ax.set_title('; '.join([str(x) for x in ps]) if isinstance(ps, tuple) else str(ps), fontsize='x-small')
        if individual_legends:
            ax.legend(fontsize='x-small')

    plt.sca(ax)
    rect = (0, 0, 0.85, 1) if legend else (0, 0, 1, 1)
    plt.tight_layout(rect=rect, pad=0.1)
    return fig, axs


class CurvedText(mpl.text.Text):
    """A text object that follows an arbitrary curve."""

    def __init__(self, x, y, text, axes, **kwargs):
        super(CurvedText, self).__init__(x[0],y[0],' ', axes, **kwargs)

        axes.add_artist(self)

        # # saving the curve:
        self.__x = x
        self.__y = y
        self.__zorder = self.get_zorder()

        # # creating the text objects
        self.__Characters = []
        for c in text:
            t = mpl.text.Text(0, 0, c, **kwargs)
            # resetting unnecessary arguments
            t.set_ha('center')
            t.set_rotation(0)
            t.set_zorder(self.__zorder +1)

            self.__Characters.append((c,t))
            axes.add_artist(t)

    # # overloading some member functions, to assure correct functionality
    # # on update
    def set_zorder(self, zorder):
        super(CurvedText, self).set_zorder(zorder)
        self.__zorder = self.get_zorder()
        for c,t in self.__Characters:
            t.set_zorder(self.__zorder+1)

    def draw(self, renderer, *args, **kwargs):
        """
        Overload of the Text.draw() function. Do not do
        do any drawing, but update the positions and rotation
        angles of self.__Characters.
        """
        self.update_positions(renderer)

    def update_positions(self,renderer):
        """
        Update positions and rotations of the individual text elements.
        """

        # preparations

        # # determining the aspect ratio:
        # # from https://stackoverflow.com/a/42014041/2454357

        # # data limits
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        # #  Axis size on figure
        figW, figH = self.axes.get_figure().get_size_inches()
        # #  Ratio of display units
        _, _, w, h = self.axes.get_position().bounds
        # # final aspect ratio
        aspect = ((figW * w)/(figH * h))*(ylim[1]-ylim[0])/(xlim[1]-xlim[0])

        # points of the curve in figure coordinates:
        x_fig,y_fig = (
            np.array(l) for l in zip(*self.axes.transData.transform([
            (i,j) for i,j in zip(self.__x,self.__y)
            ]))
        )

        # point distances in figure coordinates
        x_fig_dist = (x_fig[1:]-x_fig[:-1])
        y_fig_dist = (y_fig[1:]-y_fig[:-1])
        r_fig_dist = np.sqrt(x_fig_dist**2+y_fig_dist**2)

        # arc length in figure coordinates
        l_fig = np.insert(np.cumsum(r_fig_dist),0,0)

        # angles in figure coordinates
        rads = np.arctan2((y_fig[1:] - y_fig[:-1]),(x_fig[1:] - x_fig[:-1]))
        degs = np.rad2deg(rads)


        rel_pos = 10
        for c,t in self.__Characters:
            # finding the width of c:
            t.set_rotation(0)
            t.set_va('center')
            bbox1  = t.get_window_extent(renderer=renderer)
            w = bbox1.width
            h = bbox1.height

            # ignore all letters that don't fit:
            if rel_pos+w/2 > l_fig[-1]:
                t.set_alpha(0.0)
                rel_pos += w
                continue

            elif c != ' ':
                t.set_alpha(1.0)

            # finding the two data points between which the horizontal
            # center point of the character will be situated
            # left and right indices:
            il = np.where(rel_pos+w/2 >= l_fig)[0][-1]
            ir = np.where(rel_pos+w/2 <= l_fig)[0][0]

            # if we exactly hit a data point:
            if ir == il:
                ir += 1

            # how much of the letter width was needed to find il:
            used = l_fig[il]-rel_pos
            rel_pos = l_fig[il]

            # relative distance between il and ir where the center
            # of the character will be
            fraction = (w/2-used)/r_fig_dist[il]

            # # setting the character position in data coordinates:
            # # interpolate between the two points:
            x = self.__x[il]+fraction*(self.__x[ir]-self.__x[il])
            y = self.__y[il]+fraction*(self.__y[ir]-self.__y[il])

            # getting the offset when setting correct vertical alignment
            # in data coordinates
            t.set_va(self.get_va())
            bbox2 = t.get_window_extent(renderer=renderer)

            bbox1d = self.axes.transData.inverted().transform(bbox1)
            bbox2d = self.axes.transData.inverted().transform(bbox2)
            dr = np.array(bbox2d[0]-bbox1d[0])

            # the rotation/stretch matrix
            rad = rads[il]
            rot_mat = np.array([
                [np.cos(rad), np.sin(rad)*aspect],
                [-np.sin(rad)/aspect, np.cos(rad)]
            ])

            # # computing the offset vector of the rotated character
            drp = np.dot(dr,rot_mat)

            # setting final position and rotation:
            t.set_position(np.array([x,y])+drp)
            t.set_rotation(degs[il])

            t.set_va('center')
            t.set_ha('center')

            # updating rel_pos to right edge of character
            rel_pos += w-used

