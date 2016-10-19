#!/usr/bin/env python3

import sys
import os
from time import sleep, time, clock

from picamera import PiCamera
from PIL import Image, ImageDraw, ImageFont, ImageColor
import pygame
from pygame.locals import *

import logger
import canvas
import utilities

log = logger.create_logger(os.path.basename(__file__))
log.info('Python %s', sys.version)

# UI classes ------------------------------------------------------------------


class Box(object):

    def __init__(self, rect, **kwargs):  # add parent|canvas
        self.rect = rect  # (x, y, w, h)
        self.color = None
        self.outline = None
        for key, value in kwargs.items():
            if key == 'color':
                self.color = value
            elif key == 'outline':
                self.outline = value

    def draw(self):
        draw.rectangle((self.rect[0], self.rect[1],
                        self.rect[2]+self.rect[0]-1,
                        self.rect[3]+self.rect[1]-1),
                       fill=self.color, outline=self.outline)

    def edit(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'rect':
                self.rect = value
            elif key == 'color':
                self.color = value
            elif key == 'outline':
                self.outline = value


class TextBox(object):

    def __init__(self, rect, **kwargs):
        self.rect = rect  # Bounds
        self.color = None  # Background fill color, if any
        self.outline = None  # Outline color, if any
        self.textcolor = None  # Text color, if any
        self.callback = None  # Callback function
        self.value = None  # Value passed to callback
        for key, value in kwargs.items():
            if key == 'color':
                self.color = value
            elif key == 'outline':
                self.outline = value
            elif key == 'textcolor':
                self.textcolor = value
            elif key == 'cb':
                self.callback = value
            elif key == 'value':
                self.value = value


class Item(object):

    def __init__(self, default, **kwargs):
        self.default = default
        self.min = None
        self.max = None
        self.values = None
        self.index = None
        for key, value in kwargs.items():
            if key == 'min':
                self.min = value
            elif key == 'max':
                self.max = value
            elif key == 'values':
                self.values = value
                self.index = self.default
                if isinstance(self.values, list):
                    self.min = self.values.index(min(self.values))
                    self.max = self.values.index(max(self.values))
                if isinstance(self.values, dict):  # elif!
                    self.min = min(self.values.keys())
                    self.max = max(self.values.keys())

# Global variables ------------------------------------------------------------

ui_views = [
    'awb_mode', 'brightness', 'contrast', 'framerate', 'iso',
    'resolution', 'rotation', 'saturation', 'sharpness', 'zoom']

brightness = Item(50, min=0, max=100)

contrast = Item(0, min=-100, max=100)

zoom = Item(0, values=[1, 1.25, 1.5, 2, 3, 4, 6, 10])
log.debug(zoom.values)

iso = Item(0, values=[0, 100, 200, 320, 400, 500, 640, 800])
log.debug(iso.values)

awb_mode = Item(1, values=PiCamera._AWB_MODES_R)  # camera.AWB_MODES
log.debug('%s %s %s', awb_mode.values, awb_mode.values[awb_mode.min], awb_mode.values[awb_mode.max])

# Initialisation --------------------------------------------------------------

# PyGame init
pygame.init()
#pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_mode((320, 240), pygame.RESIZABLE)
pygame.event.set_blocked(MOUSEMOTION)
pygame.key.set_repeat(200, 200)

# OSD/HUD init
osd = Image.new('RGB', (640, 480))
draw = ImageDraw.Draw(osd)
draw.font = ImageFont.load_default()
font = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
font_size = margin_h = margin_v = osd.size[0] // 32  # = 20
draw.font = ImageFont.truetype(font, font_size)

canvas = Box((margin_h, margin_v,
              osd.size[0] - margin_h*2, osd.size[1] - margin_v*2),
             outline='green')

mybox = Box((50, 50, 150, 150), color='red', outline='white')

# PiCamera init
camera = PiCamera()
#camera.start_preview()
overlay_renderer = camera.add_overlay(
    osd.tobytes(), fullscreen=False,
    layer=4, alpha=128, size=osd.size,
    window=((camera.resolution[0]-osd.size[0]) // 2,
            (camera.resolution[1]-osd.size[1]) // 2, osd.size[0], osd.size[1]))

# Functions -------------------------------------------------------------------

def draw_box(n, qt):
    w = osd.size[0] - margin_h*2
    h = (osd.size[1] - margin_v*(qt + 1)) // qt
    origin_v = margin_v*n + h*(n - 1)

    draw.rectangle(
        (margin_h, origin_v, (w + margin_h) - 1, (origin_v + margin_v) - 1),
        fill='blue', outline='white')

def draw_text(n, qt, text, position):
    w, h = draw.textsize(text)
    origin_v = margin_v * n + 26 * (n - 1)  # box_h = 26
    if position == 0:
        draw.text((margin_h * 2, origin_v), text, 'red')
    else:
        draw.text(((osd.size[0] - w) // 2, origin_v), text, 'orange')

def update_overlay():

    param = {
        'awb_mode': camera.awb_mode,
        'brightness': camera.brightness,
        'contrast': camera.contrast,
        'framerate': camera.framerate,
        'iso': camera.iso,
        'resolution': camera.resolution,
        'rotation': camera.rotation,
        'saturation': camera.saturation,
        'sharpness': camera.sharpness,
        'zoom': camera.zoom,
        }

    # Draw background
    draw.rectangle((0, 0, osd.size[0]-1, osd.size[1]-1),
                   fill='darkblue', outline='white')

    # Draw canvas
    canvas.draw()

    mybox.draw()

    # Draw items
    for i, item in enumerate(param.items(), start=1):
        draw_box(i, len(param))
        draw_text(i, len(param), utilities.format_text(item[0]), 0)
        draw_text(i, len(param), str(item[1]), 1)

    overlay_renderer.update(osd.tobytes())

def toggle_preview():
    """Toggle camera preview"""
    if camera.preview:
        camera.stop_preview()
        overlay_renderer.alpha = 0
        pygame.display.set_mode((320, 240), pygame.RESIZABLE)
        log.info('stop preview')
    else:
        camera.start_preview()
        overlay_renderer.alpha = 128
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        log.info('start preview')

def set_brightness(direction):
    """Set brightness level"""
    old = camera.brightness
    if direction == 0:
        camera.brightness = brightness.default
    elif direction == 1 and old < brightness.max:
        camera.brightness += 1
    elif direction == -1 and old > brightness.min:
        camera.brightness -= 1
    else:
        log.info('brightness out of range!')
    #log.debug('%s > %s', old, camera.brightness)
    return camera.brightness

def set_contrast(direction):
    """Set contrast level"""
    old = camera.contrast
    if direction == 0:
        camera.contrast = contrast.default
    elif direction == 1 and old < contrast.max:
        camera.contrast += 1
    elif direction == -1 and old > contrast.min:
        camera.contrast -= 1
    else:
        log.info('contrast out of range!')
    #log.debug('%s > %s', old, camera.contrast)
    return camera.contrast

def set_iso(direction):
    """Set ISO level"""
    old = camera.iso
    if direction == 0:
        iso.index = iso.default
        camera.iso = iso.values[iso.default]
    elif direction == 1 and iso.index < iso.max:
        iso.index += 1
        camera.iso = iso.values[iso.index]
    elif direction == -1 and iso.index > iso.min:
        iso.index -= 1
        camera.iso = iso.values[iso.index]
    else:
        log.info('iso out of range!')
    log.debug('%s > %s', old, camera.iso)
    return camera.iso

def set_awb_mode(direction):
    """Set AWB mode"""
    old = camera.awb_mode
    if direction == 0:
        awb_mode.index = awb_mode.default
        camera.awb_mode = awb_mode.values[awb_mode.default]
    elif direction == 1 and awb_mode.index < awb_mode.max:
        awb_mode.index += 1
        camera.awb_mode = awb_mode.values[awb_mode.index]
    elif direction == -1 and awb_mode.index > awb_mode.min:
        awb_mode.index -= 1
        camera.awb_mode = awb_mode.values[awb_mode.index]
    else:
        log.info('awb_mode out of range!')
    #log.debug('%s > %s', old, camera.awb_mode)
    return camera.awb_mode

def set_zoom(direction):
    """Set zoom level"""
    old = zoom.values[zoom.index]
    if direction == 0:
        zoom.index = zoom.default
        camera.zoom = utilities.get_zoom_area(zoom.values[zoom.index])
    elif direction == 1 and zoom.index < zoom.max:
        zoom.index += 1
        camera.zoom = utilities.get_zoom_area(zoom.values[zoom.index])
    elif direction == -1 and zoom.index > zoom.min:
        zoom.index -= 1
        camera.zoom = utilities.get_zoom_area(zoom.values[zoom.index])
    else:
        log.info('zoom out of range!')
    #log.debug('zoom x %s', zoom.values[zoom.index])
    return camera.zoom

def quit_app():
    """Close camera and application"""
    if camera.preview:
        camera.stop_preview()
    osd.close()
    camera.close()
    pygame.quit()
    log.info('exit program')
    sys.exit()

# Main function ---------------------------------------------------------------

def main():

    update_overlay()

    running = True

    while running:

        # Process input
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE: running = False
                elif event.key == K_F1: toggle_preview()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: set_contrast(1)
                elif event.button == 2: set_zoom(0)
                elif event.button == 3: set_contrast(-1)
                elif event.button == 4: set_zoom(1)
                elif event.button == 5: set_zoom(-1)
                update_overlay()

        sleep(0.1)

    quit_app()

if __name__ == '__main__':
    main()
