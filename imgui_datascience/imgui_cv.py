import cv2
import copy
import xxhash
import numpy as np
import imgui
import OpenGL.GL as gl
from .static_vars import *
from timeit import default_timer as timer
from . import imgui_ext
import math
from typing import *
from dataclasses import dataclass

_start = timer()

USE_FAST_HASH = True

LOG_GPU_USAGE = False

"""
Some type synonyms in order to make the code easier to understand
"""
TextureId = int # this is an openGl texture id
Image_RGB = np.ndarray # denotes a RGB image
Image_AnyType = np.ndarray # denotes any image contained in a np.ndarray
ImageAddress = int # this is the image memory address


def _is_close(a: float, b: float) -> bool:
    return math.fabs(a - b) < 1E-6


# noinspection PyShadowingNames
class ImageAdjustments:
    factor: float
    delta: float
    def __init__(self, factor: float = 1., delta: float = 0.):
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

    def __hash__(self):
        return hash((self.factor, self.delta))

    def __eq__(self, other):
        return self.factor == other.factor and self.delta == other.delta


def _hash_image(image):
    """
    Two hash variant are possible :
    - if imgui_cv.USE_FAST_HASH is True : select 100 random pixels and hash them
    - otherwise : compute the hash of the whole image (using xxhash for performance)
    :param image:
    :return:hash
    """
    if USE_FAST_HASH:
        rng = np.random.RandomState(89)
        inds = rng.randint(low=0, high=image.size, size=100)
        b = image.flat[inds]
        result = hash(tuple(b.data))
        return result
    else:
        # cf https://stackoverflow.com/questions/16589791/most-efficient-property-to-hash-for-numpy-array
        h = xxhash.xxh64()
        h.update(image)
        result = h.intdigest()
        h.reset()
        return result


class ImageAndAdjustments:
    image: Image_AnyType
    image_adjustment: ImageAdjustments
    def __init__(self, image, image_adjustments):
        self.image = image
        self.image_adjustments = image_adjustments

    def adjusted_image(self):
        return self.image_adjustments.adjust(self.image)

    def __hash__(self):
        hash_adjust = hash(self.image_adjustments)
        hash_image = _hash_image(self.image)
        result = hash((hash_adjust, hash_image))
        return result

    def __eq__(self, other):
        """
        For performance reasons, the __eq__ operator is made to take only the hash into account.
        @see _image_to_texture()
        """
        hash1 = hash(self)
        hash2 = hash(other)
        return hash1 == hash2


class SizePixel:
    width: int
    height: int
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

# ALL_TEXTURES contains a dict of all the images that were transferred to the GPU
# plus their last access time

TimeSecond = float


NB_GEN_TEXTURES = 0

def _generate_texture_id() -> TextureId:
    texture_id = gl.glGenTextures(1)
    if LOG_GPU_USAGE:
        global NB_GEN_TEXTURES
        NB_GEN_TEXTURES = NB_GEN_TEXTURES + 1
        print(f"NB_GEN_TEXTURES = {NB_GEN_TEXTURES}")
    return texture_id


@dataclass
class ImageStoredOnGpu:
    image_and_adjustments: ImageAndAdjustments
    texture_id: TextureId
    time_last_access: TimeSecond = -10000.
    def __init__(self, image_and_adjustments: ImageAndAdjustments, time_last_access):
        self.image_and_adjustments = image_and_adjustments
        self.time_last_access = time_last_access
        self.texture_id = _generate_texture_id()

AllTexturesDict = Dict[ImageAddress, ImageStoredOnGpu]
ALL_TEXTURES: AllTexturesDict = {}


def _to_rgb_image(img: Image_AnyType) -> Image_RGB:
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

NB_REFRESH_TEXTURES = 0
def _image_rgb_to_texture_impl(img_rgb: Image_RGB, texture_id: TextureId):
    """
    Performs the actual transfer to the gpu and returns a texture_id
    """
    # inspired from https://www.programcreek.com/python/example/95539/OpenGL.GL.glPixelStorei (example 3)
    if LOG_GPU_USAGE:
        global NB_REFRESH_TEXTURES
        NB_REFRESH_TEXTURES = NB_REFRESH_TEXTURES + 1
        print(f"NB_REFRESH_TEXTURES = {NB_REFRESH_TEXTURES}")
    width = img_rgb.shape[1]
    height = img_rgb.shape[0]

    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_BGR, gl.GL_UNSIGNED_BYTE, img_rgb)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return texture_id




def _image_to_texture(
    image_and_adjustments: ImageAndAdjustments,
    always_refresh: bool,
    linked_user_image_address: ImageAddress
    ):
    """
    _image_to_texture will transfer the image to the GPU and return a texture Id
    Some GPU might choke if too many textures are transferred.
    For this reason :
      - a cache is maintained (ALL_TEXTURES)
      - a quick comparison is made before the transfer:
      @see _hash_image()
      @see ImageAndAdjustments.__eq__() : for performance reasons, the __eq__ operator
      is made to take only the hash into account.
    :param image_and_adjustments:
    :return: texture_id
    """
    now = timer()
    if linked_user_image_address == 0:
        image_address = id(image_and_adjustments.image)
    else:
        image_address = linked_user_image_address

    shall_refresh = False

    if image_address not in ALL_TEXTURES:
        ALL_TEXTURES[image_address] = ImageStoredOnGpu(image_and_adjustments, now)
        shall_refresh = True

    if always_refresh:
        shall_refresh = True

    image_stored_on_gpu: ImageStoredOnGpu = ALL_TEXTURES[image_address]
    image_stored_on_gpu.time_last_access = now

    if shall_refresh:
        image_and_adjustments_copy = copy.deepcopy(image_and_adjustments)
        img_adjusted = image_and_adjustments_copy.adjusted_image()
        img_rgb = _to_rgb_image(img_adjusted)
        _image_rgb_to_texture_impl(img_rgb, image_stored_on_gpu.texture_id)
    return image_stored_on_gpu.texture_id


def _clear_all_cv_textures():
    global ALL_TEXTURES
    all_textures_updated = {}
    textures_to_delete = []
    now = timer()
    for image_address, image_stored_on_gpu in ALL_TEXTURES.items():
        age_seconds = now - image_stored_on_gpu.time_last_access
        if age_seconds < 0.3:
            all_textures_updated[image_address] = image_stored_on_gpu
        else:
            textures_to_delete.append(image_stored_on_gpu.texture_id)
    ALL_TEXTURES = all_textures_updated
    if len(textures_to_delete) > 0:
        gl.glDeleteTextures(textures_to_delete)
        # print("Delete {0} old texture(s), len={1}".format(len(textures_to_delete), len(ALL_TEXTURES)))


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
def _image_impl(
    image_and_ajustments,
    width=None, height=None, title="",
    always_refresh = False,
    linked_user_image_address: ImageAddress = 0
    ):

    statics = _image_impl.statics
    statics.last_shown_image = image_and_ajustments
    zoom_key = imgui_ext.make_unique_label(title)
    if zoom_key not in statics.zoomed_status:
        statics.zoom_click_times[zoom_key] = 0
        statics.zoomed_status[zoom_key] = False
    if statics.zoomed_status[zoom_key]:
        viewport_size = SizePixel.from_image(image_and_ajustments.image)
    else:
        viewport_size = _image_viewport_size(image_and_ajustments.image, width, height)

    if zoom_key not in statics.zoomed_status:
        statics.zoomed_status[zoom_key] = False
        statics.zoom_click_times[zoom_key] = timer()

    texture_id = _image_to_texture(
        image_and_ajustments,
        always_refresh = always_refresh,
        linked_user_image_address=linked_user_image_address
        )
    if title == "":
        imgui.image_button(texture_id, viewport_size.width, viewport_size.height, frame_padding=0)
        is_mouse_hovering = imgui.is_item_hovered()
    else:
        imgui.begin_group()
        imgui.image_button(texture_id, viewport_size.width, viewport_size.height, frame_padding=0)
        is_mouse_hovering = imgui.is_item_hovered()
        imgui.text(title)
        imgui.end_group()

    if is_mouse_hovering and imgui.get_io().mouse_down[0]:
        last_time = statics.zoom_click_times[zoom_key]
        now = timer()
        if now - last_time > 0.3:
            statics.zoomed_status[zoom_key] = not statics.zoomed_status[zoom_key]
            statics.zoom_click_times[zoom_key] = now

    return mouse_position_last_image()


def image(
    img,
    width=None,
    height=None,
    title="",
    image_adjustments=None,
    always_refresh = False,
    linked_user_image_address: ImageAddress = 0
    ):

    if image_adjustments is None:
        image_adjustments = ImageAdjustments()
    image_and_ajustments = ImageAndAdjustments(img, image_adjustments)
    return _image_impl(
        image_and_ajustments,
        width=width, height=height,
        title=title,
        always_refresh = always_refresh,
        linked_user_image_address = linked_user_image_address
        )


def _is_in_image(pixel, image_shape):
    # type : (imgui.Vec2, shape) -> Bool
    w = image_shape[1]
    h = image_shape[0]
    x = pixel.x
    y = pixel.y
    return x >= 0 and x < w and y >= 0 and y < h


def _is_in_last_image(pixel):
    last_image_shape = _image_impl.statics.last_shown_image.image.shape
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
                   image_adjustments=None,
                   always_refresh = False
                   ):
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
        hide_buttons=hide_buttons,
        always_refresh = always_refresh
        )
    imgui.end_group()
    return mouse_location_original_image
