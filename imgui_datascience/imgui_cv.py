import cv2
import numpy as np
import imgui
import OpenGL.GL as gl
from .static_vars import *
from timeit import default_timer as timer
from . import imgui_ext
import math

_start = timer()


def _is_close(a, b):
    return math.fabs(a - b) < 1E-6


# noinspection PyShadowingNames
class ImageAdjustments:
    def __init__(self, factor=1., delta=0.):
        self.factor = factor
        self.delta = delta

    def is_none(self):
        return _is_close(self.factor, 1.) and _is_close(self.delta, 0.)

    def adjust(self, image):
        if self.is_none():
            return image
        else:
            adjusted = ((image + self.delta) * self.factor).astype(image.dtype)
            return adjusted


class SizePixel:
    def __init__(self, width=0, height=0):
        self.width = int(width)
        self.height = int(height)

    @staticmethod
    def from_image(image):
        self = SizePixel()
        self.width = image.shape[1]
        self.height = image.shape[0]
        return self

    def as_tuple_width_height(self):
        return self.width, self.height


def _to_rgb_image(img):
    img_rgb = None
    if len(img.shape) >= 3:
        channels = img.shape[2]
    else:
        channels = 1
    if channels == 1:
        if img.dtype == np.uint8:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.dtype in [np.float32, np.float64]:
            img_grey = np.uint8(img * 255.)
            img_rgb = cv2.cvtColor(img_grey, cv2.COLOR_GRAY2BGR)
    elif channels == 3:
        if not img.dtype == np.uint8:
            raise ValueError("imgui_cv does only support uint8 images with multiple channels")
        img_rgb = img
    elif channels == 4:
        if not img.dtype == np.uint8:
            raise ValueError("imgui_cv does only support uint8 images with multiple channels")
        # we do not handle alpha very well...
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img_rgb


# inspired from https://www.programcreek.com/python/example/95539/OpenGL.GL.glPixelStorei (example 3)
@static_vars(all_cv_textures=[])
def _image_to_texture(img, image_adjustments):
    img_adjusted = image_adjustments.adjust(img)
    img_rgb = _to_rgb_image(img_adjusted)

    width = img.shape[1]
    height = img.shape[0]
    texture_id = gl.glGenTextures(1)
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_BGR, gl.GL_UNSIGNED_BYTE, img_rgb)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

    _image_to_texture.statics.all_cv_textures.append(texture_id)
    return texture_id


def _clear_all_cv_textures():
    gl.glDeleteTextures(_image_to_texture.statics.all_cv_textures)
    _image_to_texture.statics.all_cv_textures = []


def _image_viewport_size(image, width=None, height=None):
    image_width = image.shape[1]
    image_height = image.shape[0]
    if (width is not None) and (height is not None):
        viewport_size = SizePixel(width, height)
    elif width is not None:
        viewport_size = SizePixel(width, round(image_height / image_width * width))
    elif height is not None:
        viewport_size = SizePixel(round(image_width / image_height * height), height)
    else:
        viewport_size = SizePixel.from_image(image)
    return viewport_size


@static_vars(
    zoomed_status={},
    zoom_click_times={},
    last_shown_image=None)
def _image_impl(img, image_adjustments, width=None, height=None, title=""):
    statics = _image_impl.statics
    statics.last_shown_image = img
    zoom_key = imgui_ext.make_unique_label(title)
    if zoom_key not in statics.zoomed_status:
        statics.zoom_click_times[zoom_key] = 0
        statics.zoomed_status[zoom_key] = False
    if statics.zoomed_status[zoom_key]:
        viewport_size = SizePixel.from_image(img)
    else:
        viewport_size = _image_viewport_size(img, width, height)

    if zoom_key not in statics.zoomed_status:
        statics.zoomed_status[zoom_key] = False
        statics.zoom_click_times[zoom_key] = timer()

    texture_id = _image_to_texture(img, image_adjustments)
    if title == "":
        imgui.image_button(texture_id, viewport_size.width, viewport_size.height, frame_padding=0)
        is_mouse_hovering = imgui.is_item_hovered_rect()
    else:
        imgui.begin_group()
        imgui.image_button(texture_id, viewport_size.width, viewport_size.height, frame_padding=0)
        is_mouse_hovering = imgui.is_item_hovered_rect()
        imgui.text(title)
        imgui.end_group()

    if is_mouse_hovering and imgui.get_io().mouse_down[0]:
        last_time = statics.zoom_click_times[zoom_key]
        now = timer()
        if now - last_time > 0.3:
            statics.zoomed_status[zoom_key] = not statics.zoomed_status[zoom_key]
            statics.zoom_click_times[zoom_key] = now

    return mouse_position_last_image()


def image(img, width=None, height=None, title="", image_adjustments=None):
    if image_adjustments is None:
        image_adjustments = ImageAdjustments()
    return _image_impl(img, image_adjustments, width=width, height=height, title=title)


def _is_in_image(pixel, image_shape):
    # type : (imgui.Vec2, shape) -> Bool
    w = image_shape[1]
    h = image_shape[0]
    x = pixel.x
    y = pixel.y
    return x >= 0 and x < w and y >= 0 and y < h


def _is_in_last_image(pixel):
    last_image_shape = _image_impl.statics.last_shown_image.shape
    return _is_in_image(pixel, last_image_shape)


def mouse_position_last_image():
    io = imgui.get_io()
    mouse = io.mouse_pos
    rect_min = imgui.get_item_rect_min()
    mouse_relative = imgui.Vec2(mouse.x - rect_min.x, mouse.y - rect_min.y)
    if not _is_in_last_image(mouse_relative):
        return None
    else:
        return mouse_relative


def is_mouse_hovering_last_image():  # only works if the image was presented in its original size
    if not imgui.is_item_hovered_rect():
        return False
    mouse = mouse_position_last_image()
    if mouse is None:
        return False
    else:
        return True


def image_explorer(image, width=None, height=None, title="", zoom_key="", hide_buttons=False,
                   image_adjustments=None):
    """
    :param image_adjustments:
    :param hide_buttons:
    :param image: opencv / np image.
    :param width:
    :param height:
    :param title: an optional title
    :param zoom_key: Set the same zoom_key for two image if you want to link their zoom settings
    :return: mouse location in image coordinates (None if the mouse is outside of the image)
    """
    if image_adjustments is None:
        image_adjustments = ImageAdjustments()
    from ._imgui_cv_zoom import image_explorer_autostore_zoominfo
    viewport_size = _image_viewport_size(image, width, height)
    imgui.begin_group()
    mouse_location_original_image = image_explorer_autostore_zoominfo(
        image,
        viewport_size,
        title,
        zoom_key,
        image_adjustments,
        hide_buttons=hide_buttons)
    imgui.end_group()
    return mouse_location_original_image
