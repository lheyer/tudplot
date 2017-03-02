# TUDPlot

A package for matplotlib plotting in the corporate style of the TU Darmstadt.

## Installation

Make sure dependencies are installed:

*   Python 3.5
*   matplotlib
*   numpy

Then in the source directory run:

    python3 setup.py install

## Usage

Use the function `activate` to activate TU styled plotting:

    import tudplot
    tudplot.activate()

A call with no arguments will activate a nominal color range of 6 distinct TU colors.
One can specify the keyword `full` to enable a range of continuous colors from the full TU color spectrum.

    tudplot.activate(full=10)

TUDPlot also comes with a basic exporter `saveagr`, to save the current matplotlib figure in xmgrace agr format.

    from matplotlib import pyplot as plt
    fig = plt.figure()
    fig.plot([1,2,3], label='Test')
    # Do more plotting here...
    # When the figure is complete:
    tudplot.saveagr('test.agr')
