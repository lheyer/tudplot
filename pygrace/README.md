# Pygrace: A tool to convert matplotlib figure to xmgrace plots

After plotting the matplotlib figure, call
	pygrace.saveagr('myfig.agr')
to save it as a xmgrace plot.

## Current state of supperted matplotlib porperties

The conversion is done by the appropriate classes (`AgrFigure`, `AgrAxis`, ...) defined in the pygrace module.
They each only support a small subset of matplotlib properties, see below.

### Figures

- canvas size (page size), controllable with `AgrFigure.dpi`
- font size scaling, controllable with `AgrFigure.fontscale`
- map colors
- x/y offset: adds an offset (as fraction of the according edge) to the xmgrace figure. Helpfull if x labels get pushed out of the page.

### Axes

- size, axis limits
- title
- linear or log scale
- labels and ticklabels:
  - turn on/off
  - position (left, right, bottom, top)
  - fontsize
- legend:
  - turn on/off
  - location
  - fontsize

### Lines

- label (for legend)
- linestyle
- line color
- markers:
  - shape
  - color
  - edgewidth
  - fill (appart from full and none, this is kind of random)

### Texts:

- location
- fontsize
- color
  