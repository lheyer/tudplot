# TUDPlot

A package for matplotlib plotting in the corporate style of the TU Darmstadt.

## Installation

Install dependencies:

* Python 3
* matplotlib
* seaborn

In the source directory run:

    python3 setup.py install

## Usage

The package changes the plotting style on import.
Therefore it is used by simply importing it in the python script:

    import tudplot

TUDPlot also comes with a very basic exporter, to save matplotlib figures as xmgrace agr file.
In this example, matplotlib is imported as mpl:

    fig = mpl.figure()
    fig.plot([1,2,3], label='Test')
    # Do more plotting here...
    # When the figre is complete:
    tudplot.export_to_agr(fig, 'test.agr')
