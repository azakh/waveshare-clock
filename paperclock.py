import datetime
import logging
import os

import babel
import babel.dates
import tzlocal

import weather
import drawing


# EPD_WIDTH = 400
# EPD_HEIGHT = 300
EPD_WIDTH = 264
EPD_HEIGHT = 176


class PaperClock(object):

    def __init__(self, debug_mode=False):
        self._debug_mode = debug_mode

        if not debug_mode:
            self._display_type = os.environ.get("EPAPER_TYPE", "epd2in7")
            if self._display_type == "epd2in7":
                import epd2in7
                self._display_width = epd2in7.EPD_HEIGHT  # inversed
                self._display_height = epd2in7.EPD_WIDTH
                self._epd = epd2in7.EPD()
                self._epd.init()
            elif self._display_type == "epd4in2":
                import epd4in2
                self._display_width = epd4in2.EPD_WIDTH
                self._display_height = epd4in2.EPD_HEIGHT
                self._epd = epd4in2.EPD()
                self._epd.init()
            else:
                raise "Invalid display config"
        else:
            self._display_width = EPD_WIDTH
            self._display_height = EPD_HEIGHT

        self._time_zone = tzlocal.get_localzone()
        self._str_time = "XXXX"
        self._drawing = drawing.Drawing(
            self._display_width, self._display_height)

    def display_buffer(self, buf):
        if self._debug_mode:
            buf.save("debug.bmp")
            return

        self._epd.display_frame(
            self._epd.get_frame_buffer(buf)
        )

    def update_for_datetime(self):
        dt = datetime.datetime.now(self._time_zone)
        formatted = babel.dates.format_time(
            dt,
            "HHmm",
            tzinfo=self._time_zone
        )

        # Update only once per minute
        if formatted == self._str_time:
            return

        w = weather.get_weather()
        frame = self._drawing.draw_frame(
            formatted,
            w
        )
        self.display_buffer(frame)
        self._str_time = formatted
