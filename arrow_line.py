#!/usr/bin/env python
# From http://old.nabble.com/Arrows-using-Line2D-and-shortening-lines-td19104579.html,
# accessed 2010/11/12

from matplotlib.lines import Line2D

class ArrowLine(Line2D):
    """A matplotlib subclass to draw an arrowhead on a line

    arrow (= None):                 Type of arrow (e.g., '>') (TODO: Confirm this)
    arrowsize (= 2*4):              Size of arrow
    arrowedgecolor (= 'b'):         Color of arrow edge
    arrowfacecolor (= 'b'):         Color of arrow face
    arrowedgewidth (= 4):           Width of arrow edge
    arrowheadwidth (= arrowsize):   Width of arrow head
    arrowheadlength (= arrowsize):  Length of arrow head
    *args, **kwargs:                Propagated to matplotlib.lines.Line2D
    """
    __author__ = "Jason Grout"
    __copyright__ = "Copyright (C) 2008"
    __email__ = "jason-sage@..."
    __license__ = "Modified BSD License"

    from matplotlib.path import Path

    arrows = {'>' : '_draw_triangle_arrow'}
    _arrow_path = Path([[0.0, 0.0], [-1.0, 1.0], [-1.0, -1.0], [0.0, 0.0]],
                  codes=[Path.MOVETO, Path.LINETO,Path.LINETO, Path.CLOSEPOLY])

    def __init__(self, *args, **kwargs):
        """Initialize the line and arrow.
        """
        self._arrow = kwargs.pop('arrow', None)
        self._arrowsize = kwargs.pop('arrowsize', 2*4)
        self._arrowedgecolor = kwargs.pop('arrowedgecolor', 'b')
        self._arrowfacecolor = kwargs.pop('arrowfacecolor', 'b')
        self._arrowedgewidth = kwargs.pop('arrowedgewidth', 4)
        self._arrowheadwidth = kwargs.pop('arrowheadwidth', self._arrowsize)
        self._arrowheadlength = kwargs.pop('arrowheadlength', self._arrowsize)
        Line2D.__init__(self, *args, **kwargs)

    def draw(self, renderer):
        """Draw the line and arrowhead using the passed renderer.
        """
        #if self._invalid:
        #    self.recache()
        renderer.open_group('arrowline2d')
        if not self._visible: return

        Line2D.draw(self, renderer)

        if self._arrow is not None:
            gc = renderer.new_gc()
            self._set_gc_clip(gc)
            gc.set_foreground(self._arrowedgecolor)
            gc.set_linewidth(self._arrowedgewidth)
            gc.set_alpha(self._alpha)
            funcname = self.arrows.get(self._arrow, '_draw_nothing')
        if funcname != '_draw_nothing':
            tpath, affine = self._transformed_path.get_transformed_points_and_affine()
            arrowFunc = getattr(self, funcname)
            arrowFunc(renderer, gc, tpath, affine.frozen())

        renderer.close_group('arrowline2d')

    def _draw_triangle_arrow(self, renderer, gc, path, path_trans):
        """Draw a triangular arrow.
        """
        from math import atan2
        from matplotlib.transforms import Affine2D

        segment = [i[0] for i in path.iter_segments()][-2:]
        startx,starty = path_trans.transform_point(segment[0])
        endx,endy = path_trans.transform_point(segment[1])
        angle = atan2(endy-starty, endx-startx)
        halfwidth = 0.5*renderer.points_to_pixels(self._arrowheadwidth)
        length = renderer.points_to_pixels(self._arrowheadlength)
        transform = Affine2D().scale(length,halfwidth).rotate(angle).translate(endx,endy)

        rgbFace = self._get_rgb_arrowface()
        renderer.draw_path(gc, self._arrow_path, transform, rgbFace)

    def _get_rgb_arrowface(self):
        """Get the color of the arrow face.
        """
        from matplotlib.cbook import is_string_like
        from matplotlib.colors import colorConverter

        facecolor = self._arrowfacecolor
        if is_string_like(facecolor) and facecolor.lower() == 'none':
            rgbFace = None
        else:
            rgbFace = colorConverter.to_rgb(facecolor)
        return rgbFace
