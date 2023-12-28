import re
import json
from typing import Union, Dict, Any, List, Tuple


def validate_ip(ip: str) -> bool:
    # Regex for validating an IP address
    ip_regex = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    return ip_regex.match(ip) is not None


def timecode_to_float(timecode: str, fps: int) -> float:
    hh, mm, ss, ff = map(int, timecode.split(':'))
    return hh * 3600 + mm * 60 + ss + ff / fps


def float_to_timecode(seconds: float, fps: float) -> str:
    hh = int(seconds // 3600)
    seconds %= 3600
    mm = int(seconds // 60)
    seconds %= 60
    ss = int(seconds)
    ff = int((seconds - ss) * fps)

    return f"{hh:02}:{mm:02}:{ss:02}:{ff:02}"


def parse_json(json_string: str) -> Union[Dict[str, Any], None]:
    try:
        response = json.loads(json_string)
        return response
    except json.JSONDecodeError:
        return None
