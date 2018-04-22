Features
========

Display numpy.ndarray (aka opencv image)
----------------------------------------
The following types are supported : ``RGB, RGBA, GRAY, float32, float64``

Code::

    # returns mouse_position
    imgui_cv.image(img, height=150, title="flowers")

Display matplotlib figures
--------------------------

    .. image:: images/mplot.jpg

Code::

    figure = matplotlib.pyplot.figure()
    x = numpy.arange(0.1, 100, 0.1)
    y = numpy.sin(x) / x
    plot.plot(x, y)

    imgui_fig.fig(figure, height=250, title="f(x) = sin(x) / x")


Inspect images
--------------
  * show pixels color (or float values)
  * adjust visibility for float images
  * save images
  * zoom & pan (with possible sync between 2 images)

    .. image:: images/image_explorer.jpg

See https://www.youtube.com/watch?v=yKw7VaQNFCI&feature=youtu.be for an animated demo.

Code::

    imgui_cv.image_explorer(img)


A simple way to run imgui programs
----------------------------------

The simplest way to run a program a start adding gui buttons is shown below

Code::

    def gui_loop():
        imgui.button("Click me")

    def main():
        imgui_runner.run(gui_loop, imgui_runner.Params())


A simple way to quickly inspect images
--------------------------------------

Below is the simplest to quickly display any type of numpy array (RGB, float, etc) and to be able to inspect it.

Code::

        image = ... # cv2.imread("...")
        ImGuiImageLister.push_image("owl", image)
        ImGuiLister_ShowStandalone()

.. image:: images/image_lister.png

Full demo
--------


View the full demo (1'50") on youtube by clicking on the link below

.. image:: images/thumb.jpg

https://www.youtube.com/watch?v=qstEZyLGsTQ&feature=youtu.be
