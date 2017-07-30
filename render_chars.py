#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import base64
import json
import os
import os.path as path
import sys

import cairo
import pango
import pangocairo


FONT_HEIGHT = 48


"""
Creates a new cairo.ImageSurface with the specified height and automatic width
based on the string and renders said string to the image.
"""
def render_string_to_image(string, height):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, height * 4 * len(string), height)
    context = cairo.Context(surf)

    # Do some font metrics wizardry
    pangocairo_context = pangocairo.CairoContext(context)
    layout = pangocairo_context.create_layout()
    font = pango.FontDescription("Sans")
    font.set_absolute_size(height * pango.SCALE)
    layout.set_font_description(font)
    layout.set_text(string)
    exts = layout.get_pixel_extents()
    width = exts[1][2] + -exts[0][0]

    # Draw a background rectangle:
    context.rectangle(0, 0, width, height)
    context.set_source_rgb(1, 1, 1)
    context.fill()

    # Draw the text
    context.translate(-exts[0][0], -exts[0][1])
    context.set_source_rgb(0, 0, 0)
    pangocairo_context.update_layout(layout)
    pangocairo_context.show_layout(layout)

    # Crop the rendered image
    cropped = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
    cropped_context = cairo.Context(cropped)
    cropped_context.rectangle(0, 0, width, height)
    cropped_context.set_source_surface(surf, 0, 0);
    cropped_context.fill()

    return cropped


"""
Encodes a cairo.ImageSurface to a 1-bit image.

The first byte is the width of the image.
The second byte is the height of the image.
Each subsequent byte encodes 8 pixels from left to right. 0 is black, 1 is white.
"""
def encode_image(image):
    width = image.get_width()
    height = image.get_height()
    assert width <= 0xffff
    assert height <= 0xff
    assert image.get_format() == cairo.FORMAT_RGB24

    buf = bytearray([0x00] * (width * height / 8 + 3))
    buf[0] = chr(width >> 8)
    buf[1] = chr(width & 0xff)
    buf[2] = chr(height)
    for x in range(width):
        for y in range(height):
            i = y * width + x
            pixel_r = image.get_data()[i * image.get_stride() / image.get_width()]
            a = bytearray(pixel_r)[0]
            buf[3 + i // 8] |= 0 if a > 127 else (1 << (i % 8))
    return buf


face = json.load(open(path.join(path.dirname(__file__), "face.json")))

for comp_name in face.keys():
    font_object = bytearray()
    comp_list = []
    for item in face[comp_name]:
        for i, s in enumerate(item):
            image = render_string_to_image(s, FONT_HEIGHT)

            binary_raster = encode_image(image)
            l = len(binary_raster)
            assert l <= 0xffff
            font_object += bytearray([
                0 if i == 0 else 1,
                l >> 8,
                l & 0xff,
            ])
            font_object += binary_raster

    with open(path.join(path.dirname(__file__), "lenny_%s.png" % comp_name), "wb") as f:
        f.write(font_object)
