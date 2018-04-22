import imgui
import os
from collections import OrderedDict
from inspect import getsourcefile
from os.path import abspath

this_script_dir = os.path.dirname(abspath(getsourcefile(lambda: 0)))


class FontId(object):
    Font_10, Font_14, Font_18, Font_22, Font_26, Font_30 = range(6)

    @staticmethod
    def all_fonts_dict():
        return OrderedDict([
            ('Font_10', FontId.Font_10),
            ('Font_14', FontId.Font_14),
            ('Font_18', FontId.Font_18),
            ('Font_22', FontId.Font_22),
            ('Font_26', FontId.Font_26),
            ('Font_30', FontId.Font_30)
        ])


_ALL_LOADED_FONTS = {}


def _load_one_font(font_size, font_file="source-sans-pro.regular.ttf", font_dir=this_script_dir):
    io = imgui.get_io()
    if font_dir == "":
        font_dir = "./"
        if not os.path.exists(font_dir + "/" + font_file):
            font_dir = os.path.dirname(__file__)

    if not os.path.exists(font_dir + "/" + font_file):
        raise Exception("Could not find font file")
    font = io.fonts.add_font_from_file_ttf(font_dir + "/" + font_file, font_size)
    return font


# def _LoadFontAwesome(font_size, font_file ="fontawesome-webfont.ttf", font_dir =""):
#     io = imgui.get_io()
#     if font_dir == "":
#         font_dir = os.path.dirname(__file__)
#
#     icon_ranges = [IconsFontAwesome.ICON_MIN_FA, IconsFontAwesome.ICON_MAX_FA]
#     # TypeError: Argument 'glyph_ranges' has incorrect type (expected imgui.core._StaticGlyphRanges, got list)
#     font = io.fonts.add_font_from_file_ttf(font_dir + "/" + font_file, font_size, icon_ranges)
#     return font


def push_font(font_id):
    global _ALL_LOADED_FONTS
    imgui.push_font(_ALL_LOADED_FONTS[font_id])


def push_default_font():
    push_font(FontId.Font_18)


def pop_font():
    imgui.pop_font()


def _load_fonts():
    global _ALL_LOADED_FONTS
    io = imgui.get_io()
    io.fonts.add_font_default()
    _ALL_LOADED_FONTS[FontId.Font_10] = _load_one_font(10)
    _ALL_LOADED_FONTS[FontId.Font_14] = _load_one_font(14)
    _ALL_LOADED_FONTS[FontId.Font_18] = _load_one_font(18)
    _ALL_LOADED_FONTS[FontId.Font_22] = _load_one_font(22)
    _ALL_LOADED_FONTS[FontId.Font_26] = _load_one_font(26)
    _ALL_LOADED_FONTS[FontId.Font_30] = _load_one_font(30)
    # _ALL_LOADED_FONTS[FontId.FontAwesome_30] = _LoadFontAwesome(30)


_ALL_UNIQUE_LABELS = []


def make_unique_label(label, object_id=None):
    global _ALL_UNIQUE_LABELS
    if object_id is None:
        object_id = str(len(_ALL_UNIQUE_LABELS))
    result = label + "##" + object_id
    _ALL_UNIQUE_LABELS.append(result)
    return result


def make_unique_empty_label():
    return make_unique_label("")


def __clear_all_unique_labels():
    global _ALL_UNIQUE_LABELS
    _ALL_UNIQUE_LABELS = []


def make_label_plus_icon(label, icon):
    global _ALL_UNIQUE_LABELS
    result = label + icon + "##" + len(_ALL_UNIQUE_LABELS)
    _ALL_UNIQUE_LABELS.add(result)
    return result


def make_icon_plus_label(icon, label):
    global _ALL_UNIQUE_LABELS
    result = icon + label + "##" + len(_ALL_UNIQUE_LABELS)
    _ALL_UNIQUE_LABELS.add(result)
    return result


class TogglableWindowParams:
    def __init__(self, window_title="", initial_show=True, size=(0, 0), pos=(0, 0)):
        self.window_title = window_title
        self.toggle_button_legend = ""
        self.size = size
        self.initialShow = initial_show
        self.pos = pos
        self.include_begin_code = True


_ALL_TOGGLABLE_STATUS = {}


def show_togglable_window(window_param, window_function_code):
    global _ALL_TOGGLABLE_STATUS
    if window_param.window_title not in _ALL_TOGGLABLE_STATUS:
        _ALL_TOGGLABLE_STATUS[window_param.window_title] = window_param.initialShow

    this_window_open_status = _ALL_TOGGLABLE_STATUS[window_param.window_title]

    if this_window_open_status:
        toggle_button_legend = "Hide " + window_param.window_title
    else:
        toggle_button_legend = "Show " + window_param.window_title

    if imgui.button(make_unique_label(toggle_button_legend)):
        this_window_open_status = not this_window_open_status

    if this_window_open_status:
        imgui.set_next_window_size(window_param.size[0], window_param.size[1])
        if window_param.include_begin_code:
            imgui.begin(window_param.window_title)

        window_function_code()

        if window_param.include_begin_code:
            imgui.end()


def togglable_window_toggle(window_title, open_window=None):
    global _ALL_TOGGLABLE_STATUS
    if open_window is None:
        _ALL_TOGGLABLE_STATUS[window_title] = not _ALL_TOGGLABLE_STATUS[window_title]
    else:
        _ALL_TOGGLABLE_STATUS[window_title] = open_window


def togglable_window_get_status(window_title):
    global _ALL_TOGGLABLE_STATUS
    return _ALL_TOGGLABLE_STATUS[window_title]


def listbox_dict(dict_string_value, current_key, title_top="", title_right="", height_in_items=20, item_width=None):
    keys = [key for key, _ in dict_string_value.items()]
    if current_key in keys:
        current_idx = keys.index(current_key)
    else:
        current_idx = -1
    if item_width is not None:
        imgui.push_item_width(item_width)
    if title_top != "":
        imgui.text(title_top)
    changed, new_idx = imgui.listbox(title_right, current_idx, keys, height_in_items=height_in_items)
    if 0 <= new_idx < len(keys):
        new_key = keys[new_idx]
    else:
        new_key = ""
    return changed, new_key
