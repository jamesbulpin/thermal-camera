#!/usr/bin/env python3
import sys
import socket
import colorsys

from PIL import Image, ImageDraw, ImageFont
import ST7789 as ST7789
from mlx90640_devicetree import *
from mlx90640 import *

font = ImageFont.load_default()

ip_attempts = 0
def get_ip():
    global ip_attempts
    if ip_attempts > 20:
        return None
    ip_attempts = ip_attempts + 1
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = None
    finally:
        s.close()
    return ip

ip = get_ip()

def setup_mlx90640():
    print("start")
    dev = MLX90640()
    print("dev", dev)

    r = dev.i2c_init("/dev/i2c-1")
    print("init", r)
    r = dev.set_refresh_rate(1)
    print("setRefreshRate", r)

    refresh_rate = dev.get_refresh_rate()
    print("refresh rate: {}".format(refresh_rate))

    dev.dump_eeprom()
    dev.extract_parameters()
    return dev

dev = setup_mlx90640()

def loop(dev):
    global ip
    while True:
        dev.get_frame_data()
        ta = dev.get_ta() - 8.0
        emissivity = 1
        to = dev.calculate_to(emissivity, ta)

        image = Image.new('RGB', (32, 32), color='grey')
        pixels = image.load()
        c = 0.0
        for x in range(32):
            for y in range(24):
                t = to[y*32 + x];
                c = c + t
                t = (30.0-t)*7.0
                if t < 0:
                    t = 0
                if t > 240:
                    t = 240.0
                r, g, b = colorsys.hsv_to_rgb(t/360.0,1,1)
                pixels[x,23-y] = (int(r*255), int(g*255), int(b*255))
        image = image.resize((WIDTH, HEIGHT))
        d = ImageDraw.Draw(image)
        txt = "Mean: " + format(c/768.0, ".1f") + "C"
        d.text((10, 190), txt, font=font, fill=(255, 255, 255, 255))
        txt = "Centre: " + format(to[12*32 + 16], ".1f") + "C"
        d.text((10, 210), txt, font=font, fill=(255, 255, 255, 255))
        if ip != None:
            d.text((120, 190), ip, font=font, fill=(255, 255, 255, 255))
        else:
            ip = get_ip()
        disp.display(image)

# Create ST7789 LCD display class.
disp = ST7789.ST7789(
        height=240,
        rotation=90,
        port=0,
        cs=1,
        dc=9,
        backlight=19,
        spi_speed_hz=60 * 1000 * 1000,
        offset_left=0,
        offset_top=0
    )

WIDTH = disp.width
HEIGHT = disp.height

# Initialize display.
disp.begin()

loop(dev)
