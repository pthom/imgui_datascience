from collections import OrderedDict
import imgui
from . import imgui_cv
from . import imgui_ext
from . import imgui_fig


def image_size_fit_in_gui(image_size, gui_size, can_make_bigger=False):
    # type: (imgui.Vec2, imgui.Vec2, bool) -> imgui.Vec2
    if image_size.x <= gui_size.x and image_size.y <= gui_size.y and not can_make_bigger:
        return image_size
    else:
        k_item = image_size.x / image_size.y
        k_gui = gui_size.x / gui_size.y
        if k_item > k_gui:
            return imgui.Vec2(gui_size.x, image_size.y / image_size.x * gui_size.x)
        else:
            return imgui.Vec2(image_size.x / image_size.y * gui_size.y, gui_size.y)


class _ImguiImageInfo:
    def __init__(self, image, additional_legend, image_adjustments):
        self.image = image
        self.additional_legend = additional_legend
        self.image_adjustments = image_adjustments


class _ImguiImageLister:
    """
    Do not instantiate this class by yourself, use the global instance named ImguiImageLister
    """

    def __init__(self):
        self.images_info = OrderedDict()
        self.current_image = ""
        self.opened = False
        self.never_shown = True
        self.listbox_width = 240
        self.position = imgui.Vec2(500, 50)
        self.window_size = imgui.Vec2(1000, 800)
        self.max_size = False

    def show_toggle_window_button(self, show_at_startup=False):
        if show_at_startup and self.never_shown:
            self.opened = True
        self.never_shown = False
        if self.opened:
            if imgui.button("Hide image lister"):
                self.opened = False
        else:
            if imgui.button("Show image lister"):
                self.opened = True

    def push_image(self, name, image, additional_legend="", image_adjustments=imgui_cv.ImageAdjustments()):
        image_type_name = type(image).__name__
        if image_type_name == "Figure":
            as_image = imgui_fig._fig_to_image(image)
        else:
            as_image = image
        self.images_info[name] = _ImguiImageInfo(as_image, additional_legend, image_adjustments)

    def clear_all_images(self):
        self.images_info = OrderedDict()
        self.current_image = ""

    def _set_selected_image(self, key):
        self.current_image = key

    def _show_list(self):
        imgui.begin_group()
        # imgui.text("")
        changed, selected_key = imgui_ext.listbox_dict(self.images_info, self.current_image, title_top="Images",
                                                       height_in_items=40, item_width=self.listbox_width)
        if changed:
            self._set_selected_image(selected_key)
        if imgui.button(imgui_ext.make_unique_label("Clear all")):
            self.clear_all_images()
        imgui.end_group()

    def _max_image_size(self):
        win_size = imgui.get_window_size()
        max_image_size = imgui.Vec2(win_size.x - (self.listbox_width + 40), win_size.y - 150)
        return max_image_size

    def _show_image(self):
        if self.current_image in self.images_info:
            imgui.begin_group()
            if imgui.button("X"):
                self.images_info.pop(self.current_image)
                self.current_image = ""
            else:
                image_info = self.images_info[self.current_image]
                if image_info.additional_legend != "":
                    imgui.same_line()
                    imgui.text(image_info.additional_legend)
                img = image_info.image
                image_size = imgui.Vec2(img.shape[1], img.shape[0])
                image_size = image_size_fit_in_gui(image_size, self._max_image_size(), can_make_bigger=True)
                imgui_cv.image_explorer(img, title=self.current_image,
                                        width=int(round(image_size.x)), height=int(round(image_size.y)),
                                        image_adjustments=image_info.image_adjustments)
            imgui.end_group()

    def actual_window_startup_size(self):
        if self.max_size:
            display_size = imgui.get_io().display_size
            return imgui.Vec2(display_size.x - 40, display_size.y - 20)
        else:
            return self.window_size

    def _select_first_image(self):
        items = list(self.images_info.items())
        if len(items) > 0:
            self.current_image = items[0][0]

    def _heartbeat(self):
        if not self.opened:
            return
        if self.current_image == "":
            self._select_first_image()
        imgui.set_next_window_position(self.position.x, self.position.y, imgui.APPEARING)
        imgui.set_next_window_size(self.actual_window_startup_size().x, self.actual_window_startup_size().y,
                                   imgui.APPEARING)
        expanded, self.opened = imgui.begin("Imgui Image Lister")
        self._show_list()
        imgui.same_line()
        self._show_image()
        imgui.end()


ImGuiImageLister = _ImguiImageLister()
