#!/usr/bin/env python3

import sys
from time import sleep, time, clock
from fractions import Fraction
from picamera import PiCamera
from PIL import Image, ImageDraw, ImageFont, ImageColor
import pygame
from pygame.locals import *
import logger

import utilities

# UI classes ------------------------------------------------------------------

class TextBox:

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


class Item:

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
            elif key == 'index':
                self.index = value
        if (isinstance(self.values, list)):
            self.min = self.values[0]
            self.max = self.values[-1]

# Global variables ------------------------------------------------------------

ui_views = [
    'brightness', 'contrast', 'framerate', 'hflip', 'iso',
    'resolution', 'rotation', 'saturation', 'sharpness', 'vflip']

zoom = Item((0.0, 0.0, 1.0, 1.0),
            values=[1, 2, 3, 4, 5, 8, 10, 16, 20], index=0)

brightness = Item(50, min=0, max=100)

contrast = Item(0, min=-100, max=100)

iso = Item(0, values=[0, 100, 200, 320, 400, 500, 640, 800], index=0)

awb_mode = Item('auto', values=PiCamera.AWB_MODES)  # camera.AWB_MODES
logger.info(awb_mode.values)

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
font_size = margin_h = margin_v = osd.size[0] // 32
draw.font = ImageFont.truetype(font, font_size)

# PiCamera init
camera = PiCamera()
#camera.start_preview()
overlay_renderer = camera.add_overlay(
    osd.tostring(), fullscreen=False,
    layer=4, alpha=128, size=osd.size,
    window=((camera.resolution[0]-osd.size[0]) // 2,
            (camera.resolution[1]-osd.size[1]) // 2, osd.size[0], osd.size[1]))

# Functions -------------------------------------------------------------------

def draw_box(n, qt):
    w = osd.size[0] - margin_h*2
    h = (osd.size[1] - margin_v*(qt + 1)) // qt
    origin_v = margin_v*n + h*(n - 1)
    draw.rectangle((margin_h, origin_v, w + margin_h, origin_v + margin_v),
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
        'brightness': camera.brightness,
        'contrast': camera.contrast,
        'framerate': camera.framerate,
        'hflip': camera.hflip,
        'iso': camera.iso,
        'resolution': camera.resolution,
        'rotation': camera.rotation,
        'saturation': camera.saturation,
        'sharpness': camera.sharpness,
        'vflip': camera.vflip,
        }

    draw.rectangle((0, 0, osd.size[0]-1, osd.size[1]-1),
                   fill='darkblue', outline='white')

    for i, item in enumerate(param.items(), start=1):
        draw_box(i, len(param))
        draw_text(i, len(param), utilities.format_text(item[0]), 0)
        draw_text(i, len(param), str(item[1]), 1)

    overlay_renderer.update(osd.tostring())

def toggle_preview():
    """Toggles camera preview"""
    if camera.preview:
        camera.stop_preview()
        overlay_renderer.alpha = 0
        pygame.display.set_mode((320, 240), pygame.RESIZABLE)
        logger.info('stop preview')
    else:
        camera.start_preview()
        overlay_renderer.alpha = 128
        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        logger.info('start preview')

def set_brightness(direction):
    """Sets brightness level"""
    old = camera.brightness
    if direction == 0:
        camera.brightness = brightness.default
    elif direction == 1 and old < brightness.max:
        camera.brightness += 1
    elif direction == -1 and old > brightness.min:
        camera.brightness -= 1
    else:
        logger.info('brightness out of range!')
    #logger.info('%s > %s', old, camera.brightness)
    return camera.brightness

def set_contrast(direction):
    """Sets contrast level"""
    old = camera.contrast
    if direction == 0:
        camera.contrast = contrast.default
    elif direction == 1 and old < contrast.max:
        camera.contrast += 1
    elif direction == -1 and old > contrast.min:
        camera.contrast -= 1
    else:
        logger.info('contrast out of range!')
    #logger.info('%s > %s', old, camera.contrast)
    return camera.contrast

def set_iso(direction):
    """Sets ISO level"""
    old = camera.iso
    if direction == 0:
        iso.index = 0
        camera.iso = iso.default
    elif direction == 1 and old < iso.max:
        iso.index += 1
        camera.iso = iso.values[iso.index]
    elif direction == -1 and old > iso.min:
        iso.index -= 1
        camera.iso = iso.values[iso.index]
    else:
        logger.info('iso out of range!')
    #logger.info(%s > %s', old, camera.iso)
    return camera.iso

def set_awb_mode(direction):
    """Sets AWB mode"""
    old = camera.awb_mode
    if direction == 0:
        camera.awb_mode = awb_mode.default
    elif direction == 1 and old < contrast.max:
        camera.awb_mode += 1
    elif direction == -1 and old > contrast.min:
        camera.awb_mode -= 1
    else:
        logger.info('awb_mode out of range!')
    #logger.info('%s > %s', old, camera.awb_mode)
    return camera.awb_mode

def set_zoom(direction):
    """Sets zoom level"""
    old = zoom.values[zoom.index]
    if direction == 0:
        zoom.index = 0
        camera.zoom = zoom.default
    elif direction == 1 and old < zoom.max:
        zoom.index += 1
        w = h = Fraction(1, zoom.values[zoom.index])
        x = y = Fraction(1 - w, 2)
        camera.zoom = (x, y, w, h)
    elif direction == -1 and old > zoom.min:
        zoom.index -= 1
        w = h = Fraction(1, zoom.values[zoom.index])
        x = y = Fraction(1 - w, 2)
        camera.zoom = (x, y, w, h)
    else:
        logger.info('zoom out of range!')
    #logger.info('zoom x %s', zoom.values[zoom.index])
    return camera.zoom

def quit_app():
    """Cleanly closes camera and application"""
    if camera.preview:
        camera.stop_preview()
    osd.close()
    camera.close()
    pygame.quit()
    logger.info('exit program')
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
                elif event.button == 2: set_iso(0)
                elif event.button == 3: set_contrast(-1)
                elif event.button == 4: set_iso(1)
                elif event.button == 5: set_iso(-1)
                update_overlay()

        sleep(0.1)

    quit_app()

if __name__ == '__main__':
    main()
