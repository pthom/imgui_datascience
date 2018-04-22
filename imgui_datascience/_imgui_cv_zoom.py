from __future__ import division
from enum import Enum
import numpy as np
import numpy.linalg
import imgui
from . import imgui_ext
from . import imgui_cv
from .imgui_cv import SizePixel
from .static_vars import *
import cv2
import math


def _is_close(a, b):
    return math.fabs(a - b) < 1E-6


def compute_zoom_matrix(zoom_center, zoom_ratio):
    mat = np.eye(3)
    mat[0, 0] = zoom_ratio
    mat[1, 1] = zoom_ratio
    mat[0, 2] = zoom_center.x * (1. - zoom_ratio)
    mat[1, 2] = zoom_center.y * (1. - zoom_ratio)
    return mat


def compute_pan_matrix(drag_delta, current_zoom):
    mat = np.eye(3)
    mat[0, 2] = drag_delta.x / current_zoom
    mat[1, 2] = drag_delta.y / current_zoom
    return mat


def m33_to_m23(m):
    r = np.zeros((2, 3))
    for y in range(0, 2):
        for x in range(0, 3):
            r[y, x] = m[y, x]
    return r


class ZoomOrPan(Enum):
    Pan = "Pan"
    Zoom = "Zoom"


class ZoomInfo:
    def __init__(self):
        self.affine_transform = np.eye(3)
        self.zoom_or_pan = ZoomOrPan.Pan
        self.last_delta = imgui.Vec2(0., 0.)

    def set_scale_one(self, image_size, viewport_size):
        self.affine_transform = np.eye(3)
        self.affine_transform[0, 2] = (viewport_size.width / 2 - image_size.width / 2)
        self.affine_transform[1, 2] = (viewport_size.height / 2 - image_size.height / 2)

    def set_full_view(self, image_size, viewport_size):
        k_image = image_size.width / image_size.height
        k_viewport = float(viewport_size.width) / float(viewport_size.height)
        if k_image > k_viewport:
            zoom = float(viewport_size.width) / float(image_size.width)
        else:
            zoom = float(viewport_size.height) / float(image_size.height)
        self.affine_transform = np.eye(3)
        self.affine_transform[0, 0] = zoom
        self.affine_transform[1, 1] = zoom

    @staticmethod
    def make_full_view(image_size, viewport_size):
        _ = ZoomInfo()
        _.set_full_view(image_size, viewport_size)
        return _

    def mouse_location_original_image(self, mouse_location):  # -> imgui.Vec2:
        mouse2 = np.array([[mouse_location.x], [mouse_location.y], [1.]])
        pt_original = np.dot(numpy.linalg.inv(self.affine_transform), mouse2)
        return imgui.Vec2(pt_original[0, 0], pt_original[1, 0])


class ImageWithZoomInfo:
    def __init__(self, image, viewport_size, zoom_info=None, hide_buttons=False,
                 image_adjustments=None):
        if image_adjustments is None:
            image_adjustments = imgui_cv.ImageAdjustments()
        self.image = image
        self.original_viewport_size = viewport_size
        self.force_viewport_size = False
        self.hide_buttons = hide_buttons
        self.image_adjustments = image_adjustments
        self.show_adjustments = False
        self.filename = ""
        self.zoom_info = ZoomInfo()

        if zoom_info is None:
            self.reset_zoom_info()
        else:
            self.zoom_info = zoom_info

    def can_show_big_viewport(self):
        s1 = SizePixel.from_image(self.image)
        s2 = self.original_viewport_size
        return (s1.width != s2.width) or (s1.height != s2.height)

    def is_not_full_view(self):
        fullview_affine_transform = ZoomInfo.make_full_view(
            SizePixel.from_image(self.image), self.current_viewport_size()).affine_transform
        current_affine_transform = self.zoom_info.affine_transform
        diff = np.absolute(fullview_affine_transform - current_affine_transform).max()
        return diff > 1E-6

    def reset_zoom_info(self):
        self.zoom_info.set_full_view(SizePixel.from_image(self.image), self.current_viewport_size())

    def current_viewport_size(self):
        if self.force_viewport_size:
            return SizePixel.from_image(self.image)
        else:
            return self.original_viewport_size

    def get_force_viewport_size(self):
        return self.force_viewport_size

    def set_force_viewport_size(self, value):
        self.force_viewport_size = value
        self.reset_zoom_info()

    def zoomed_image(self):
        m = m33_to_m23(self.zoom_info.affine_transform)
        zoomed = cv2.warpAffine(self.image, m, self.current_viewport_size().as_tuple_width_height(),
                                flags=cv2.INTER_NEAREST)
        return zoomed

    def viewport_center_original_image(self):  # -> imgui.Vec2:
        center = np.array([[self.current_viewport_size().width / 2.], [self.current_viewport_size().height / 2.], [1.]])
        center_original = np.dot(
            numpy.linalg.inv(self.zoom_info.affine_transform),
            center)
        return imgui.Vec2(center_original[0, 0], center_original[1, 0])


def _display_zoom_or_pan_buttons(im):  # : ImageWithZoomInfo):
    # display zoom or pan radio buttons
    current_mode = im.zoom_info.zoom_or_pan
    if imgui.radio_button(imgui_ext.make_unique_label("drag to pan"), current_mode == ZoomOrPan.Pan):
        im.zoom_info.zoom_or_pan = ZoomOrPan.Pan
    imgui.same_line()
    if imgui.radio_button(imgui_ext.make_unique_label("drag to zoom"), current_mode == ZoomOrPan.Zoom):
        im.zoom_info.zoom_or_pan = ZoomOrPan.Zoom


def color_msg(color):
    msg = ""
    if isinstance(color, np.uint8):
        msg = "{0}".format(color)
    elif isinstance(color, np.float32):
        msg = "{0:.3f}".format(color)
    elif isinstance(color, np.float64):
        msg = "{0:.3f}".format(color)
    else:
        if len(color) == 3:
            bgr = color
            imgui.color_button(bgr[2] / 255., bgr[1] / 255., bgr[0] / 255.)
            imgui.same_line()
            msg = "RGB({0},{1},{2})".format(bgr[2], bgr[1], bgr[0])
        elif len(color) == 4:
            bgra = color
            imgui.color_button(bgra[2] / 255., bgra[1] / 255., bgra[0] / 255., bgra[3])
            imgui.same_line()
            msg = "RGBA({0},{1},{2},{3})".format(bgra[2], bgra[1], bgra[0], bgra[3])
    return msg


# noinspection PyArgumentList,PyArgumentList
def image_explorer_impl(im, title=""):
    # type: (ImageWithZoomInfo, str) -> None
    """
    :return: imgui.Vec2 (mouse_location_original_image) or None (if not on image)
    """

    if im.image.size == 0:
        imgui.text("empty image !")
        return imgui.Vec2(0, 0)

    zoomed_image = im.zoomed_image()

    if not im.hide_buttons:
        _display_zoom_or_pan_buttons(im)
        if title != "":
            imgui.same_line()
            imgui.text("     " + title)
    mouse_location = imgui_cv.image(zoomed_image, image_adjustments=im.image_adjustments)
    mouse_location_original_image = None
    viewport_center_original_image = im.viewport_center_original_image()

    if not im.hide_buttons and mouse_location is not None:
        mouse_drag_button = 0
        is_mouse_dragging = imgui.is_mouse_dragging(mouse_drag_button) and imgui.is_item_hovered()
        drag_delta = imgui.get_mouse_drag_delta(mouse_drag_button)

        mouse_location_original_image = im.zoom_info.mouse_location_original_image(mouse_location)

        # Handle dragging / zoom or pan
        if not is_mouse_dragging:
            im.zoom_info.last_delta = imgui.Vec2(0, 0)
        if is_mouse_dragging:
            drag_delta_delta = imgui.Vec2(drag_delta.x - im.zoom_info.last_delta.x,
                                          drag_delta.y - im.zoom_info.last_delta.y)

            if im.zoom_info.zoom_or_pan == ZoomOrPan.Zoom:
                k = 1.03
                if drag_delta.y < 0:
                    zoom_ratio = k
                else:
                    zoom_ratio = 1. / k
                im.zoom_info.affine_transform = np.dot(
                    im.zoom_info.affine_transform,
                    compute_zoom_matrix(mouse_location_original_image, zoom_ratio))

            if im.zoom_info.zoom_or_pan == ZoomOrPan.Pan:
                im.zoom_info.affine_transform = np.dot(
                    im.zoom_info.affine_transform,
                    compute_pan_matrix(drag_delta_delta, im.zoom_info.affine_transform[0, 0])
                )

            im.zoom_info.last_delta = drag_delta

    # Zoom & Pan buttons

    def perform_zoom(ratio):
        im.zoom_info.affine_transform = np.dot(
            im.zoom_info.affine_transform,
            compute_zoom_matrix(viewport_center_original_image, ratio)
        )

    import functools
    perform_zoom_plus = functools.partial(perform_zoom, 1.25)
    perform_zoom_minus = functools.partial(perform_zoom, 1. / 1.25)

    def perform_scale_one():
        im.zoom_info.set_scale_one(SizePixel.from_image(im.image), im.current_viewport_size())

    def perform_full_view():
        im.zoom_info.set_full_view(SizePixel.from_image(im.image), im.current_viewport_size())

    def perform_force_viewport_size():
        im.set_force_viewport_size(True)

    def perform_reset_viewport_size():
        im.set_force_viewport_size(False)

    def perform_hide_buttons():
        im.hide_buttons = True

    def perform_show_buttons():
        im.hide_buttons = False

    def show_zoom_button(name, action, same_line=True):
        if imgui.small_button(imgui_ext.make_unique_label(name)):
            action()
        if same_line:
            imgui.same_line()

    if im.hide_buttons:
        show_zoom_button("+", perform_show_buttons, False)
        imgui.same_line()
        imgui.text(title)
    else:
        show_zoom_button("-", perform_hide_buttons)
    if not im.hide_buttons:
        show_zoom_button("zoom +", perform_zoom_plus)
        show_zoom_button("zoom -", perform_zoom_minus)
        if im.can_show_big_viewport():
            show_zoom_button("scale 1", perform_scale_one)
        if im.is_not_full_view():
            show_zoom_button("full view", perform_full_view)
        if not im.show_adjustments:
            if imgui.small_button(imgui_ext.make_unique_label("Adjust")):
                im.show_adjustments = True
        # adjustments
        if im.show_adjustments:
            imgui.new_line()
            imgui.text("Adjust:")
            imgui.same_line()
            imgui.push_item_width(80)
            # noinspection PyArgumentList
            changed, im.image_adjustments.factor = imgui.slider_float(
                imgui_ext.make_unique_label("k"), im.image_adjustments.factor, 0., 32., display_format="%.3f", power=5.)
            imgui.same_line()
            imgui.push_item_width(80)
            changed, im.image_adjustments.delta = imgui.slider_float(
                imgui_ext.make_unique_label("delta"), im.image_adjustments.delta, 0., 255., display_format="%.3f", power=5.)
            imgui.same_line()
            if not im.image_adjustments.is_none():
                if imgui.small_button(imgui_ext.make_unique_label("reset")):
                    im.image_adjustments = imgui_cv.ImageAdjustments()
            imgui.same_line()
            if imgui.small_button(imgui_ext.make_unique_label("hide adjust")):
                im.show_adjustments = False
        # Show image info
        image_type_msg = str(im.image.dtype) + str(im.image.shape)
        zoom = im.zoom_info.affine_transform[0, 0]
        import math
        if not _is_close(zoom, 1):
            zoom_msg = "Zoom:{0:.2f} ".format(zoom)
        else:
            zoom_msg = ""
        msg = zoom_msg + image_type_msg
        imgui.text(msg)

        if im.can_show_big_viewport():
            imgui.same_line()
            if im.get_force_viewport_size():
                show_zoom_button("reset viewport", perform_reset_viewport_size)
            else:
                show_zoom_button("fit viewport", perform_force_viewport_size)
            imgui.new_line()
        # Save button
        # imgui.same_line()
        imgui.push_item_width(60)
        changed, im.filename = imgui.input_text(imgui_ext.make_unique_label(""), im.filename, 1000)
        imgui.same_line()
        if imgui.small_button(imgui_ext.make_unique_label("save")):
            cv2.imwrite(im.filename, im.image)
        # Show pixel color info
        if mouse_location is not None:
            color = zoomed_image[int(round(mouse_location.y)), int(round(mouse_location.x))]

            mouse2 = np.array([[mouse_location.x], [mouse_location.y], [1.]])
            pt_original = np.dot(numpy.linalg.inv(im.zoom_info.affine_transform), mouse2)
            position_msg = "({0},{1})".format(int(round(pt_original[0, 0])), int(round(pt_original[1, 0])))
            imgui.text(position_msg + " " + color_msg(color))
        else:
            imgui.text("")

    return mouse_location_original_image


@static_vars(
    all_ImageWithZoomInfo={},
    all_zoom_info={}
)
def image_explorer_autostore_zoominfo(image, viewport_size, title, zoom_key, image_adjustments, hide_buttons):
    statics = image_explorer_autostore_zoominfo.statics
    image_key = imgui_ext.make_unique_label(title)
    if zoom_key == "":
        zoom_key = image_key
    if viewport_size is None:
        viewport_size = SizePixel.from_image(image)
    if zoom_key not in statics.all_zoom_info:
        statics.all_zoom_info[zoom_key] = ZoomInfo.make_full_view(SizePixel.from_image(image), viewport_size)

    flag_need_update = False
    if image_key not in statics.all_ImageWithZoomInfo:
        flag_need_update = True
    elif id(statics.all_ImageWithZoomInfo[image_key].image) != id(image):
        flag_need_update = True

    if flag_need_update:
        statics.all_ImageWithZoomInfo[image_key] = ImageWithZoomInfo(
            image,
            viewport_size,
            statics.all_zoom_info[zoom_key],
            hide_buttons=hide_buttons,
            image_adjustments=image_adjustments)

    return image_explorer_impl(statics.all_ImageWithZoomInfo[image_key], title)

