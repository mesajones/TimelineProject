import re
import json
from typing import Union, Dict, Any, List, Tuple

from config.settings import TIMECODE_FPS


def validate_ip(ip: str) -> bool:
    # Regex for validating an IP address
    ip_regex = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    return ip_regex.match(ip) is not None


def timecode_to_float(timecode: str, fps: int = TIMECODE_FPS) -> float:
    hh, mm, ss, ff = map(int, timecode.split(':'))
    return hh * 3600 + mm * 60 + ss + ff / fps


def float_to_timecode(seconds: float, fps: float = TIMECODE_FPS) -> str:
    hh = int(seconds // 3600)
    seconds %= 3600
    mm = int(seconds // 60)
    seconds %= 60
    ss = int(seconds)
    ff = int((seconds - ss) * fps)

    return f"{hh:02}:{mm:02}:{ss:02}:{ff:02}"


PIXEL_TO_SECOND_FACTOR = 60


def timecode_to_position(timecode, zoom_factor, offset=0):
    """
    Convert a timecode float to a pixel position.

    :param timecode: Timecode float.
    :param zoom_factor: Current zoom level of the timeline.
    :param offset: Offset in pixels if the timeline is scrolled.
    :return: Pixel position.
    """
    # Example conversion logic
    pixels_per_second = PIXEL_TO_SECOND_FACTOR * zoom_factor  # Adjust this scale as needed
    position = timecode * pixels_per_second + offset
    return position


def position_to_timecode(position, zoom_factor, offset=0):
    """
    Convert a pixel position to a timecode float.

    :param position: Pixel position on the timeline.
    :param zoom_factor: Current zoom level of the timeline.
    :param offset: Offset in pixels if the timeline is scrolled.
    :return: Timecode float.
    """
    pixels_per_second = PIXEL_TO_SECOND_FACTOR * zoom_factor  # Should be consistent with timecode_to_position
    timecode = (position - offset) / pixels_per_second
    return timecode


def parse_json(json_string: str) -> Union[Dict[str, Any], None]:
    try:
        response = json.loads(json_string)
        return response
    except json.JSONDecodeError:
        return None
