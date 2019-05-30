# -*- coding: utf-8 -*-

import os

from PIL import Image, ImageDraw, ImageFont

import icons


class Drawing(object):

    def __init__(self, w, h):
        self._width = w
        self._height = h

        self._margin = [int(w * 0.013), int(h * 0.013)]
        self._corner_radius = 10
        self._time_xy = [(self._margin[0], self._margin[1]),
                         (w - self._margin[0], int(h * 0.66) - self._margin[1])]
        self._weather_xy = [(self._margin[0], self._time_xy[1][1] +
                             self._margin[1]), (w - self._margin[0], h - self._margin[1])]
        self._img = Image.new('1', (self._width, self._height), 1)
        self._draw = ImageDraw.Draw(self._img)
        self._time_font = self.calibrate_font('./font/RobotoCondensed-Bold.ttf',
                                              (self._time_xy[1][0] - self._time_xy[0][0], self._time_xy[1][1] - self._time_xy[0][1]), self._margin[0], "0000")
        self._big_weather_font = self.calibrate_font('./font/RobotoCondensed-Regular.ttf',
                                                     (int((self._weather_xy[1][0] - self._weather_xy[0][0]) / 3), self._weather_xy[1][1] - self._weather_xy[0][1]), self._margin[0], u"-00")
        self._weather_font = self.calibrate_font('./font/RobotoCondensed-Regular.ttf',
                                                 (int((self._weather_xy[1][0] - self._weather_xy[0][0]) / 3), int((self._weather_xy[1][1] - self._weather_xy[0][1]) * 0.75)), self._margin[0], u"00.0")
        self._small_weather_font = self.calibrate_font('./font/RobotoCondensed-Regular.ttf',
                                                       (int((self._weather_xy[1][0] - self._weather_xy[0][0]) / 3), int((self._weather_xy[1][1] - self._weather_xy[0][1]) * 0.25)), self._margin[0], u"000")

    def calibrate_font(self, font_name, bounding_box, margin_x, txt):
        max_width = bounding_box[0] - margin_x * (len(txt) + 1)
        font_size = 10
        while True:
            # iterate until the text size is just larger than the criteria
            font = ImageFont.truetype(font_name, font_size)
            txt_size = font.getsize(txt)
            if (txt_size[0] >= max_width or txt_size[1] >= bounding_box[1]):
                break
            font_size += 1

        font_size -= 1
        return ImageFont.truetype(font_name, font_size)

    def draw_rounded_rectangle(self, xy, corner_radius, fill):
        upper_left_point = xy[0]
        bottom_right_point = xy[1]
        self._draw.rectangle(
            [
                (upper_left_point[0], upper_left_point[1] + corner_radius),
                (upper_left_point[0] + corner_radius,
                 bottom_right_point[1] - corner_radius)
            ],
            fill=fill
        )
        self._draw.rectangle(
            [
                (upper_left_point[0] + corner_radius, upper_left_point[1]),
                (bottom_right_point[0] - corner_radius, bottom_right_point[1])
            ],
            fill=fill
        )
        self._draw.rectangle(
            [
                (bottom_right_point[0] - corner_radius,
                 upper_left_point[1] + corner_radius),
                (bottom_right_point[0], bottom_right_point[1] - corner_radius)
            ],
            fill=fill
        )
        self._draw.pieslice([upper_left_point, (upper_left_point[0] + corner_radius * 2, upper_left_point[1] + corner_radius * 2)],
                            180,
                            270,
                            fill=fill
                            )
        self._draw.pieslice([(bottom_right_point[0] - corner_radius * 2, bottom_right_point[1] - corner_radius * 2), bottom_right_point],
                            0,
                            90,
                            fill=fill
                            )
        self._draw.pieslice([(upper_left_point[0], bottom_right_point[1] - corner_radius * 2), (upper_left_point[0] + corner_radius * 2, bottom_right_point[1])],
                            90,
                            180,
                            fill=fill
                            )
        self._draw.pieslice([(bottom_right_point[0] - corner_radius * 2, upper_left_point[1]), (bottom_right_point[0], upper_left_point[1] + corner_radius * 2)],
                            270,
                            360,
                            fill=fill
                            )

    def draw_temp(self, center_x, y, temp, temp_size, deg_size, deg_offset):
        font = self._big_weather_font
        sz = font.getsize(temp)
        self._draw.text(
            (center_x-(sz[0]/2), y),
            temp,
            font=font,
            fill=255
        )

        self._draw.text(
            (center_x+(sz[0]/2), y+deg_offset),
            u'°',
            font=font,
            fill=255
        )

    def draw_small_temp(self, center_x, y, caption):
        self.draw_temp(
            center_x,
            y,
            caption,
            80,
            40,
            10
        )

    def get_darksky_icon(self, icon_name, size):
        icon = icons.darksky[icon_name]
        fn_icon = os.path.join(
            "./icons",
            icon
        )
        img_icon = Image.open(fn_icon)
        return img_icon.resize(size, Image.LANCZOS)

    # Return position of a rectangle with size of "size"
    # which is aligned horizontally and vertically at the center of rectangle "xy"
    def get_center_aligned_pos(self, xy, size):
        return (int((xy[0][0] + xy[1][0] - size[0]) / 2), int((xy[0][1] + xy[1][1] - size[1]) / 2))

    def draw_weather_icon(self, xy, weather_icon_name):
        weather_icon_min_size = min(xy[1][0] - xy[0][0], xy[1][1] - xy[0][1])
        weather_icon_size = (weather_icon_min_size, weather_icon_min_size)
        weather_icon = self.get_darksky_icon(
            weather_icon_name, weather_icon_size)
        weather_icon_pos = self.get_center_aligned_pos(
            xy, weather_icon_size)
        self._img.paste(weather_icon, weather_icon_pos)

    def draw_center_aligned_text(self, xy, txt, font, off_y_ratio):
        pos = self.get_center_aligned_pos(xy, font.getsize(txt))
        y_offs = int(font.getsize("0")[1] * off_y_ratio)
        pos = (pos[0], pos[1] - y_offs)
        self._draw.text(pos,
                        txt,
                        font=font,
                        fill=255)

    def draw_weather_temperature(self, xy, temp):
        weather_temperature = u"{:.0f}°".format(temp)
        self.draw_center_aligned_text(
            xy, weather_temperature, self._big_weather_font, 0.13)

    def draw_weather_wind(self, xy, value, subscript):
        split_y = xy[0][1] + int((xy[1][1] - xy[0][1]) * 0.75)

        value_xy = [(xy[0][0], xy[0][1]), (xy[1][0], split_y)]
        value_txt = "{:.1f}".format(value)
        self.draw_center_aligned_text(
            value_xy, value_txt, self._weather_font, 0.13)

        subscript_xy = [(xy[0][0], split_y), (xy[1][0], xy[1][1])]
        self.draw_center_aligned_text(
            subscript_xy, subscript, self._small_weather_font, 0.13)

    def draw_weather(self, weather):
        # Background
        self.draw_rounded_rectangle(
            self._weather_xy, self._corner_radius, "black")

        margin_x = self._margin[0]
        margin_y = self._margin[1]

        # Split bottom part into 3 zones - weather icon, current temperature, wind
        zone_width = int((self._weather_xy[1][0] -
                          self._weather_xy[0][0] - margin_x * 4) / 3)
        zone_heigth = int((self._weather_xy[1][1] -
                           self._weather_xy[0][1] - margin_y * 2))
        offset_x = self._weather_xy[0][0] + margin_x
        offset_y = self._weather_xy[0][1] + margin_y

        # Weather icon area.
        weather_icon_name = "n/a" if weather is None else weather.icon
        weather_icon_xy = [(offset_x, offset_y),
                           (offset_x + zone_width, offset_y + zone_heigth)]
        self.draw_weather_icon(weather_icon_xy, weather_icon_name)
        # When no data is available N/A is enough
        if weather is None:
            return

        # Current temperature
        offset_x += zone_width + margin_x
        weather_temperature_xy = [
            (offset_x, offset_y), (offset_x + zone_width, offset_y + zone_heigth)]
        self.draw_weather_temperature(weather_temperature_xy, weather.temp)
        offset_x += zone_width + margin_x

        # Current wind speed
        weather_wind_xy = [
            (offset_x, offset_y), (offset_x + zone_width, offset_y + zone_heigth)]
        self.draw_weather_wind(weather_wind_xy, weather.wind, "m/s")

        # top_y = 194

        # self.draw_temp(150, top_y, weather_temperature, 100, 60, 9)

        # mid_y = top_y + 17

        # caption = "%0.0f" % weather.temp_min
        # self.draw_small_temp(250, mid_y, caption)

        # caption = "%0.0f" % weather.temp_max
        # self.draw_small_temp(350, mid_y, caption)

    def draw_time(self, formatted_time):
        margin_x = self._margin[0]
        y_offs = int(self._time_font.getsize("0")[1] * 0.15)
        digit_width = int((self._time_xy[1][0] - self._time_xy[0][0] -
                           margin_x * (len(formatted_time) - 1)) / len(formatted_time))
        offs = 0

        for n in formatted_time:
            xy = [(self._time_xy[0][0] + offs, self._time_xy[0][1]),
                  (self._time_xy[0][0] + offs + digit_width, self._time_xy[1][1])]
            self.draw_rounded_rectangle(xy, self._corner_radius, "black")

            digit_pos = self.get_center_aligned_pos(
                xy, self._time_font.getsize(n))
            digit_pos = (digit_pos[0], digit_pos[1] - y_offs)

            self._draw.text(digit_pos,
                            n,
                            font=self._time_font,
                            fill=255
                            )

            offs += digit_width
            offs += margin_x

    def draw_frame(self, formatted_time, weather):
        # Clear the framebuffer
        self._draw.rectangle([(0, 0), (self._width, self._height)], "white")

        # Draw time
        self.draw_time(formatted_time)

        # draw weather into buffer
        self.draw_weather(weather)

        return self._img
