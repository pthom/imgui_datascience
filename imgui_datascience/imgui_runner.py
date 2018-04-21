import sys
import imgui
from . import imgui_ext
from .imgui_image_lister import ImGuiImageLister
from . import imgui_cv

import os

import pygame
import OpenGL.GL as gl

from imgui.integrations.pygame import PygameRenderer
import imgui


class Params:
    def __init__(self, win_size=(800, 600), win_title="Imgui - Title", windowed_full_screen=False,
                 provide_default_window=True):
        self.win_size = win_size
        self.win_title = win_title
        self.windowed_full_screen = windowed_full_screen  # "Full screen", but with a window title bar + close button
        # Those params are used for windowed_full_screen mode
        self.windows_taskbar_height = 60
        self.window_title_height = 32
        self.windowed_full_screen_x_margin = 20
        self.provide_default_window = provide_default_window


_g_Imgui_extensions_root_window_size = (640, 480)


def run(gui_loop_function, params=Params()):
    if params.windowed_full_screen:
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (
            params.windowed_full_screen_x_margin / 2, params.window_title_height)

    pygame.init()
    pygame.display.set_caption(params.win_title)
    win_size = params.win_size
    if params.windowed_full_screen:
        info = pygame.display.Info()
        screen_size = (info.current_w - params.windowed_full_screen_x_margin, info.current_h)
        win_size = (screen_size[0], screen_size[1] - params.window_title_height - params.windows_taskbar_height)

    pygame.display.set_mode(win_size, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
    imgui_ext._load_fonts()

    io = imgui.get_io()
    io.display_size = win_size

    renderer = PygameRenderer()

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            renderer.process_event(event)

        imgui.new_frame()
        if params.provide_default_window:
            imgui.set_next_window_position(0, 0)
            imgui.set_next_window_size(win_size[0], win_size[1])
            imgui.begin("Default window")
        gui_loop_function()
        if params.provide_default_window:
            imgui.end()
        ImGuiImageLister._heartbeat()

        # note: cannot use screen.fill((1, 1, 1)) because pygame's screen
        #       does not support fill() on OpenGL surfaces
        gl.glClearColor(1, 1, 1, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()

        pygame.display.flip()

        imgui_cv._clear_all_cv_textures()
        imgui_ext.__clear_all_unique_labels()


def _none_gui_loop():
    pass


def ImGuiLister_ShowStandalone():
    ImGuiImageLister.window_size = imgui.Vec2(1000, 800)
    ImGuiImageLister.position = imgui.Vec2(0, 0)
    ImGuiImageLister.opened = True
    ImGuiImageLister.max_size = True

    run(_none_gui_loop, Params(win_title="ImGuiLister", windowed_full_screen=True))
