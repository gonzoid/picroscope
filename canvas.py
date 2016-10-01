#!/usr/bin/env python3
#
#  untitled.py
#  
#  Copyright 2016 Gergely Nagy <passznemtudom@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
__author__ = "Gergely Nagy"
__license__ = "GPL"
__version__ = "0.1b"
__status__ = "development"


import sys
import os
import time
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageColor

#from PIL import Image, ImageFont, ImageChops
#import image_draw_ex as ImageDraw
import logger

log = logger.create_logger(os.path.basename(__file__))
log.info('Python %s', sys.version)

# Nokia LCD screen dimensions
LCD_WIDTH = 200
LCD_HEIGHT = 100


class Canvas(object):
    """
    A GUI for the Nokia 5110 LCD screen. It features two kind of boxes:
    imageboxes and textboxes. Boxes are moveable images on the base
    image (normally a blank white/black one). Textboxes are a special
    type of boxes: they show the given text, and their image is
    generated automatically. Boxes are referenced by their unique ID.

    The class can also be used without a physical LCD screen if
    Canvas.target_LCD == None.
    """


    class Box(object):
        """
        A class that contains attributes and methods which are commons
        to all kinds of boxes.
        """


        def __init__(self):
            """
            :param image: the Image to be used as the box
            :param priority: the priority of the box, higher overlaps lower
            """
##            self.image = None
##            self.size = 0
##            self.position = (0, 0)
##            self.priority = 0
##            self.visible = True


        def invert(self):
            """Invert the image (useful for i.e. highlighting)"""

            self.image = ImageChops.invert(self.image)


        def shift(self, amount):
            """
            Move the box by the given relative coordinates
            :param amount: the horizontal and vertical amount of
                shifting in pixels, tuple
            """
            x = amount[0] + self.position[0]
            y = amount[1] + self.position[1]
            self.position = (x, y)


        def align(self, horizontal=None, vertical=None):
            """
            Move the box to the given position; set None not to change
            :param horizontal: horizontal alignment ('left', 'center',
                'right' or None)
            :param vertical: vertical alignment ('top', 'middle',
                'bottom' or None)
            """
            x, y = self.position[0], self.position[1]
            
            if horizontal == 'left':
                x = 0
            elif horizontal == 'center':
                x = (LCD_WIDTH - self.size[0])//2
            elif horizontal == 'right':
                x = LCD_WIDTH - self.size[0]

            if vertical == 'top':
                y = 0
            elif vertical == 'middle':
                y = (LCD_HEIGHT - self.size[1])//2
            elif vertical == 'bottom':
                y = LCD_HEIGHT - self.size[1]

            self.position = (x, y)


    class ImageBox(Box):
        """
        An imagebox is an image that is positioned on the canvas. The
        coordinates of it are the upper left corner's of the image, and
        defaults to (0, 0).
        """


        def __init__(self, image, priority=0):
            """
            :param image: the Image to be used as the box
            :param priority: the priority of the box, higher overlaps lower
            """
            self.image = None
            self.size = 0
            self.change_image(image)
            self.position = (0, 0)
            self.priority = priority
            self.visible = True


        def change_image(self, image):
            """
            Change the box's picture with the conversion if neccessary
            :param image: the new image of the box
            """
            self.image = image
            #if self.image.mode != '1':
                #self.image = self.image.convert(mode='1', dither=Image.NONE)
            self.size = self.image.size


    class Textbox(Box):
        """
        A special type of box that consist of a text and a frame. Size
        is auto-managed.
        """

        def __init__(self, text, text_color=None, font=None, spacing=0,
                     text_align='left', box_color=None, padding=5,
                     frame_width=0, priority=0):
            """
            :param text: the text of the box
            :param text_color: the color of the text, 0 for black on white,
                else white on black
            :param font: the font type of the text (ImageFont instance)
            :param spacing: spacing between the lines of the text
            :param text_align: align of the text within the box ('left',
                'center' or 'right')
            :param box_color: the background color of the box
            :param padding: padding between box bounds and text
            :param frame_width: the width of the frame line in pixels
            :param priority: higher overlaps lower
            ### add type attr. (like 'title') w/ std font, txt_align, etc.
            """
            self.position = (0, 0)
            self.priority = priority
            self.visible = True

            self.text = None
            self.text_color = None
            self.font = None
            self.spacing = None
            self.text_align = None
            self.box_color = None
            self.padding = None
            self.frame_width = None
            ##self.size = None
            self.image = Image.new('RGBA', (0,0))  # dummy Image for ImageDraw
            self.draw = ImageDraw.Draw(self.image)

            self.edit_properties(text, text_color, font, spacing, text_align,
                                 box_color, padding, frame_width)


        def edit_properties(self, text=None, text_color=None, font=0,
                            spacing=None, text_align=None, box_color=None,
                            padding=None, frame_width=None):
            """
            Change the box's given properties (the ones that implies
                redrawing it)
            :param text: the text of the box
            :param text_color: the color of the text, 0 for black on white,
                else white on black
            :param font: the font type of the text (ImageFont instance)
            :param spacing: spacing between the lines of the text
            :param text_align: align of the text ('left', 'center' or 'right')
            :param box_color: the background color of the box
            :param padding: padding between box bounds and text
            :param frame_width: the width of the frame line in pixels
            ### add type attr. (like 'title') w/ std font, txt_align, etc.
            """
            if text is not None:
                self.text = text
            if text_color is not None:
                self.text_color = text_color #0 if text_color==0 else 255
            if font != 0:
                self.font = font
            if spacing is not None:
                self.spacing = spacing
            if text_align is not None:
                self.text_align = text_align
            if box_color is not None:
                self.box_color = box_color
            if padding is not None:
                self.padding = padding
            if frame_width is not None:
                self.frame_width = frame_width

            x = self.draw.textsize(text, self.font)[0] + 2 * self.padding + 2 * self.frame_width
            y = self.draw.textsize(text, self.font)[1] + 2 * self.padding + 2 * self.frame_width
            self.size = (x, y)
            self.image = Image.new('RGBA', self.size, self.box_color)
                                   #(255 if self.text_color==0 else 0))
            self.draw = ImageDraw.Draw(self.image)

            text_coords = (self.frame_width + self.padding,
                           self.frame_width + self.padding)
            
            #drawing text:
            self.draw.multiline_text(text_coords, self.text,
                fill=self.text_color, font=self.font, spacing=self.spacing,
                align=self.text_align)
            #self.draw.text(...)
            
            #drawing frame:
            for i in range(self.frame_width):
                self.draw.line([(i, 0), (i, self.size[1])],
                               fill=self.text_color)  # left
                self.draw.line([(0, i), (self.size[0], i)],
                               fill=self.text_color)  # top
                self.draw.line([(self.size[0]-1-i, 0),
                                (self.size[0]-1-i, self.size[1])],
                               fill=self.text_color)  # right
                self.draw.line([(0, self.size[1]-1-i),
                                (self.size[0]), self.size[1]-1-i],
                               fill=self.text_color)  # bottom


            ### add swap_color method?


    def __init__(self, target, size, base_color=None):
        """
        :param target: the LCD instance of the target Nokia 5110 LCD
            screen (use None for debug without an LCD)
        :param base_color: 0 for black, else white (if base == None)
        :param base: the base image on what the boxes are drawn
        """
        self.LCD = target
        if self.LCD is not None:
            self.LCD.clear()
        if size is not None:
            self.size = size
        #if base_color is not None:
        self.base_color = base_color
        self.base = Image.new('RGB', self.size, self.base_color)
                              #(0 if base_color==0 else 255))

        # Dictionary of all the image boxes and textboxes. Keys are
        # the box_ids, and the values are the boxes themselves.
        self._boxes = {}


    def add_imagebox(self, box_id, image, priority=0):
        """
        Add a new box to the canvas
        :param box_id: the name of the box, should be unique
        :param image: the image of the box
        :param position: the position of the box's upper left corner)
        :param priority: the box with higher priority is drawn above
            the one with lower priority
        """
        if box_id in self._boxes.keys():
            raise ValueError("ID already exists")

        box = self.ImageBox(image, priority)
        self._boxes[box_id] = box


    def add_textbox(self, box_id, text, text_color=None, font=None, spacing=0,
                    text_align='left', box_color=None, padding=5,
                    frame_width=0, priority=0):
        """
        Add a new textbox to the boxes with the given properties
        :param box_id: the name of the box, should be unique
        :param text: the text of the box
        :param text_color: the color of the text, 0 for black on white,
            else white on black
        :param font: the font type of the text (ImageFont instance)
        :param spacing: spacing between the lines of the text
        :param text_align: align of the text ('left', 'center' or 'right')
        :param box_color: the background color of the box
        :param padding: padding between box bounds and text
        :param frame_width: the width of the frame line in pixels
        :param priority: the box with higher priority is drawn above
            the one with lower priority
        ### add type attr. (like 'title') w/ std font, txt_align, etc.
        """        
        if box_id in self._boxes.keys():
            raise ValueError("ID already exists")
        textbox = self.Textbox(text, text_color, font, spacing, text_align,
                               box_color, padding, frame_width, priority)
        self._boxes[box_id] = textbox


    def get_box(self, box_id):
        """Return the box itself, useful for reading their properties"""

        return self._boxes[box_id]


    def edit_box_image(self, box_id, image):
        """Change the box's image"""

        try:
            self._boxes[box_id].change_image(image)
        except KeyError:
            raise ValueError("Invalid box ID")
        except AttributeError as e:
            raise TypeError("edit_box_image used on a Textbox", e)


    def edit_textbox(self, box_id, text=None, text_color=None, font=0,
                     spacing=None, text_align=None, box_color=None,
                     padding=None, frame_width=None):
        """Edit the textbox box's properties. None means no change"""

        try:
            self._boxes[box_id].edit_properties(
                text, text_color, font, spacing, text_align,
                box_color, padding, frame_width)
        except KeyError:
            raise ValueError("Invalid box ID")
        except AttributeError as e:
            raise TypeError("edit_textbox called on a non-Textbox box", e)


    def set_priority(self, box_id, value):
        """Set the box's priority"""

        try:
            self._boxes[box_id].priority = value    
        except KeyError:
            raise ValueError("Invalid box ID")


    def hide_box(self, box_id):
        """Make the box hidden"""

        self._boxes[box_id].visible = False


    def show_box(self, box_id):
        """Make the box visible"""

        self._boxes[box_id].visible = True


    def set_pos(self, box_id, pos):
        """Set the box's position"""

        assert type(pos) is tuple
        try:
            self._boxes[box_id].position = pos
        except KeyError:
            raise ValueError("Invalid box ID")


    def shift(self, box_id, amount):
        """Move the box by the given amount of pixels
        :param amount: the horizontal and vertical amount of shifting in
            pixels; tuple
        """

        try:
            self._boxes[box_id].shift(amount)
        except KeyError:
            raise ValueError("Invalid box ID")


    def align(self, box_id, horizontal, vertical):
        """Align the box to the given position"""

        try:
            box = self._boxes[box_id]
            box.align(horizontal, vertical)
        except KeyError:
            raise ValueError("Invalid box ID") 


    def invert(self, box_id):
        """Invert the box's colour"""

        try:
            self._boxes[box_id].invert()
        except KeyError:
            raise ValueError("Invalid box ID")


    def delete_box(self, box_id):
        """Delete the box"""

        try:
            del self._boxes[box_id]
        except ValueError:
            raise ValueError("Invalid box ID")


    def construct_screen(self):
        """Flatten the canvas"""

        screen = self.base.copy()
        # sort the boxes according to their priorities
        sorted_boxes = sorted(self._boxes.values(), key=lambda x: x.priority)
        for box in sorted_boxes:
            screen.paste(box.image, box.position, box.image)
        #screen = screen.convert(mode='1', dither=Image.NONE)

        return screen


    def update_screen(self):
        """Output the canvas to screen"""

        screen = self.construct_screen()
        if self.LCD is not None:
            self.LCD.image(screen)
            self.LCD.display()
        else:
            # note that normally the code is runned as root, and
            # Image.show() does not work this way!
            self.construct_screen().show()


def main():
    """
    A test code that uses almost all functions of the library
    """
    lcd = None
    size = (LCD_WIDTH, LCD_HEIGHT)
    base_color = 'grey'
    canvas = Canvas(lcd, size, base_color)

    font_path = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'
    font = ImageFont.truetype(font_path, 18)

    #square = Image.new('RGBA', (10, 10), 'green')
    logo = Image.open('../images/overlay_small.png')
    canvas.add_imagebox('logo', logo, priority=5)
    canvas.align('logo', 'right', 'bottom')
    canvas.add_textbox('raoulduke', "This is\nBat country!",
                       text_align='center', frame_width=1, priority=1,
                       box_color='yellowgreen', font=font)
    #canvas.add_textbox('drgonzo', "Get your\nhead straight.",
                        #text_align='right', frame_width=3, priority=10,
                        #text_color='purple', font=font)
    canvas.add_textbox('drgonzo', "Get your\nhead straight.", priority=10,
                       font=font, text_color='purple')
    canvas.update_screen()
    time.sleep(0.5)

    canvas.align('drgonzo', 'center', 'middle')
    canvas.align('raoulduke', 'right', 'bottom')
    canvas.update_screen()
    time.sleep(0.5)

    canvas.invert('drgonzo')
    canvas.update_screen()
    time.sleep(0.5)

    canvas.set_pos('raoulduke', (10, 10))
    canvas.shift('drgonzo', (-5, 20))
    canvas.update_screen()
    time.sleep(0.5)

    rectangle = Image.new('RGBA', (10, 20), 'yellow')
    #canvas.edit_box_image('logo', rectangle)
    canvas.edit_textbox('raoulduke', text="Wait,\nyou poor fool...",
                        text_align='right', frame_width=0, box_color='orange')
    canvas.set_priority('drgonzo', 0)
    canvas.update_screen()
    time.sleep(0.5)

    # debug
    for k, v in canvas._boxes.items():
        log.debug('==== %s ====', k)
        for i in v.__dict__.items():
            log.debug(i)
            if i[0] is 'image':
                log.debug(i[1].getbands())
                log.debug(i[1].getextrema())
                #if i[1].split()[3]is not None:

    canvas.delete_box('drgonzo')
    canvas.update_screen()


if __name__=='__main__':

    main()
