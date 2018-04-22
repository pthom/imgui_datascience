from __future__ import division

from . import *  # <=> i.e from imgui_datascience import *

import cv2
from collections import deque
import os
import inspect
import numpy as np
from timeit import default_timer
from inspect import getsourcefile
from os.path import abspath


THIS_SCRIPT_DIR = os.path.dirname(abspath(getsourcefile(lambda: 0)))


@static_vars(clicked=False, check=False)
def show_buttons():
    statics = show_buttons.statics
    if imgui.button("Button"):
        statics.clicked = not statics.clicked
    if statics.clicked:
        imgui.same_line()
        imgui.text("Thanks for clicking me!")
    changed, statics.check = imgui.checkbox("checkbox", statics.check)


@static_vars(img=cv2.imread(THIS_SCRIPT_DIR + "/images/flower.jpg"))
def demo_image():
    imgui.text("This image is provided by opencv / numpy.")
    imgui.text("You can click on it to show it with its original size")
    statics = demo_image.statics
    imgui_cv.image(statics.img, height=150, title="flowers")  # returns mouse_position


def make_contour_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    normalized = np.float32(gray) / 255.
    edges = cv2.Sobel(normalized, -1, 1, 1, ksize=3) + 0.5
    return edges


@static_vars(
    img=cv2.imread(THIS_SCRIPT_DIR + "/images/billiard.jpg"),
    img_contours=None
)
def demo_image_explorer():
    statics = demo_image_explorer.statics
    if statics.img_contours is None:
        statics.img_contours = make_contour_image(statics.img)
    imgui.text("""imgui_cv.image_explorer() will show a detailed view of an opencv image.
You can zoom, pan & see the colors of the pixels.
You can optionally link the zoom of two images (using the zoom_key param)
""")
    imgui_cv.image_explorer(statics.img, zoom_key="1")
    imgui.text("image_explorer is compatible with uint8 and float images")
    imgui.text("Click the '+' button below this image in order to see more info")
    imgui.text("Then, click the 'adjust' button in order to adjust the view of a float matrix")
    imgui_cv.image_explorer(statics.img_contours, zoom_key="1", hide_buttons=True)


@static_vars(inited=False)
def demo_image_lister():
    if not demo_image_lister.statics.inited:
        for name in ["owl", "billiard", "flower"]:
            ImGuiImageLister.push_image(name, cv2.imread(THIS_SCRIPT_DIR + "/images/" + name + ".jpg"))
            demo_image_lister.statics.inited = True
    imgui.text("""The image lister enable to keep a list of images in a separate window for further examination
Just call 'ImGuiImageLister.show_toggle_window_button()' somewhere in your code, 
and add images via 'ImGuiImageLister.push_image(name, image)'""")
    ImGuiImageLister.show_toggle_window_button()


@static_vars(
    imgs={}
)
def demo_image_explorer_types():
    imgui.text("imgui_cv.image and imgui_cv.image_explorer can support multiple image types")
    imgui.separator()
    statics = demo_image_explorer_types.statics
    if len(statics.imgs) == 0:
        img = cv2.imread(THIS_SCRIPT_DIR + "/images/owl.jpg")
        img_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        statics.imgs["RGB uint8"] = img
        statics.imgs["Gray uint8"] = img_grey
        statics.imgs["Float32"] = np.float32(img_grey) / 255.
        statics.imgs["Float64"] = np.float64(img_grey) / 255.
        statics.imgs["RGBA"] = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    for key, img in statics.imgs.items():
        imgui_cv.image_explorer(img, title=key, height=200, hide_buttons=False)
        imgui.separator()


def make_figure():
    import matplotlib
    import numpy
    figure = matplotlib.pyplot.figure()
    plot = figure.add_subplot(111)
    # draw a cardinal sine plot
    x = numpy.arange(0.1, 100, 0.1)
    y = numpy.sin(x) / x
    plot.plot(x, y)
    return figure


@static_vars(figure=make_figure())
def demo_figs():
    imgui.text("opencv images of matplotlib figures can be presented as thumbnails \n(click to show the original size)")
    imgui_fig.fig(demo_figs.statics.figure, height=250, title="f(x) = sin(x) / x")


def demo_font():
    for font_name, font_id in imgui_ext.FontId.all_fonts_dict().items():
        imgui_ext.push_font(font_id)
        imgui.text(font_name)
        imgui_ext.pop_font()


def demo_original_demo():
    imgui.text("The 'ImGui Demo' window (to the right of this window) \nis a good way to learn imgui. See its code at ")
    url = "https://github.com/ocornut/imgui/blob/master/imgui_demo.cpp"
    imgui.input_text("", url, 300)
    imgui.same_line()
    if imgui.button("Open in browser"):
        import webbrowser
        webbrowser.open(url)


def demo_cpp_to_python():
    imgui.text("Below is an example of two widgets and their code")
    imgui.separator()
    show_buttons()
    imgui.separator()
    python_code = inspect.getsource(show_buttons)
    python_advice = """    
Since imgui is well suited 
with static variables,
a 'static_vars' decorator 
is provided
    """
    imgui.input_text_multiline("python code\n" + python_advice, python_code, len(python_code) * 2, 500, 150)

    imgui.text("\nThis python code is the equivalent of the following cpp code:\n\n")
    cpp_code = """void ShowButtons() 
{
    static bool clicked = false;
    if (ImGui::Button("Button")) 
        clicked = ! clicked;
    if (clicked)
    {
        ImGui::SameLine();
        ImGui::Text("Thanks for clicking me!");
    }
    static bool check = true;
    ImGui::Checkbox("checkbox", &check);
}"""
    imgui.input_text_multiline("cpp code", cpp_code, len(cpp_code) * 2, 500, 200)


def demo_this_module_code():
    module = inspect.getmodule(demo_this_module_code)
    source = inspect.getsource(module)
    imgui.input_text_multiline("", source, len(source) * 2, 700, 400)
    if imgui.button("Copy to clipboard"):
        def put_text_to_clipboard(text):
            try:
                from Tkinter import Tk  # python 2
            except ImportError:
                from tkinter import Tk  # python 3
            r = Tk()
            r.withdraw()
            r.clipboard_clear()
            r.clipboard_append(text)
            r.update()
            r.destroy()
        put_text_to_clipboard(source)


def demo_imguilister_standalone():
    def run_imguilister_standalone():
        image = cv2.imread(THIS_SCRIPT_DIR + "/images/owl.jpg")
        ImGuiImageLister.push_image("owl", image)
        ImGuiLister_ShowStandalone()

    imgui.text("""
If you only need to inspect one or serveral images with a better tool than
cv2.imshow(), all you need to write is a function like this one:
""")
    source  = inspect.getsource(run_imguilister_standalone)
    imgui.input_text_multiline(imgui_ext.make_unique_empty_label(), source, len(source) * 2, 400, 90)
    imgui.text("If you click this button, a new demo will be launched, using this code")
    if imgui.button("Demo standalone"):
        run_imguilister_standalone()


@static_vars(flag_show_code = dict())
def show_one_feature(feature_function, feature_intro, default_open=False):
    flag_show_code = show_one_feature.statics.flag_show_code
    flags = imgui.TREE_NODE_DEFAULT_OPEN if default_open else 0
    expanded, visible=imgui.collapsing_header(feature_intro, flags=flags)
    if expanded:
        imgui_ext.push_font(imgui_ext.FontId.Font_18)
        imgui.text(feature_intro)
        imgui_ext.pop_font()
        if feature_intro not in flag_show_code:
            flag_show_code[feature_intro] = False
        imgui.same_line(imgui.get_window_width() - 150)
        _, flag_show_code[feature_intro] = imgui.checkbox(imgui_ext.make_unique_label("View code"), flag_show_code[feature_intro])
        if flag_show_code[feature_intro]:
            code = inspect.getsource(feature_function)
            imgui.input_text_multiline(imgui_ext.make_unique_empty_label(), code, len(code) * 2, 600, 200)
        feature_function()


@static_vars(last_call_times=deque())
def compute_fps():
    statics = compute_fps.statics
    now = default_timer()
    statics.last_call_times.append(now)
    window_length = 24 # the computed fps is the average for the last 24 frames
    if len(statics.last_call_times) > window_length:
        last = statics.last_call_times.popleft()
        fps = float(window_length) / (now - last)
    else:
        fps = 0
    return fps


def show_fps():
    imgui.set_next_window_position(0, 0, imgui.APPEARING)
    imgui.set_next_window_size(100, 40, imgui.APPEARING)
    imgui.begin("FPS")
    msg = "{0:.1f}".format(compute_fps())
    imgui.text(msg)
    imgui.end()


def gui_loop():
    imgui.set_next_window_position(0, 40, imgui.APPEARING)
    imgui.set_next_window_size(750, 680, imgui.APPEARING)
    imgui.begin("ImGui for data scientists")
    show_fps()
    show_one_feature(demo_image, "Using opencv images (numpy.ndarray)")
    show_one_feature(demo_figs, "Using matplotlib figures")
    show_one_feature(demo_image_explorer, "Using image explorer")
    show_one_feature(demo_image_explorer_types, "Image types")
    show_one_feature(demo_image_lister, "Image Lister")
    show_one_feature(demo_imguilister_standalone, "Image Lister Standalone")
    show_one_feature(demo_font, "Using different font sizes")
    show_one_feature(demo_cpp_to_python, "Python code advices / porting from cpp ")
    show_one_feature(demo_this_module_code, "Code for this demo")
    show_one_feature(demo_original_demo, "ImGui Demo")
    imgui.end()

    imgui.set_next_window_position(750, 40, imgui.APPEARING)
    imgui.show_test_window()


def example():
    imgui_runner.run(gui_loop, imgui_runner.Params(windowed_full_screen=True, win_title="Dear Imgui !",
                                                   provide_default_window=False))
