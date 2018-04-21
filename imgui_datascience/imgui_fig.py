import numpy
import matplotlib
import matplotlib.pyplot
import cv2
from . import imgui_cv
from .static_vars import static_vars

@static_vars(fig_cache = dict())
def _fig_to_image(fig):
    statics = _fig_to_image.statics
    fig_id = id(fig)
    if not fig_id in statics.fig_cache:
        # draw the renderer
        fig.canvas.draw()
        # Get the RGBA buffer from the figure
        w, h = fig.canvas.get_width_height()
        buf = numpy.fromstring(fig.canvas.tostring_rgb(), dtype=numpy.uint8)
        buf.shape = (h, w, 3)
        img_rgb = cv2.cvtColor(buf, cv2.COLOR_RGB2BGR)
        matplotlib.pyplot.close(fig)
        statics.fig_cache[fig_id] = img_rgb
    return statics.fig_cache[fig_id]

def fig(figure, width = None, height = None, title=""):
    image =_fig_to_image(figure)
    return imgui_cv.image(image, width = width, height = height, title=title)


