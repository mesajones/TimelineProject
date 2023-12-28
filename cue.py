from dataclasses import dataclass, field
from typing import List, Optional

from utils import timecode_to_float, float_to_timecode
from config.settings import FPS


@dataclass
class Cue:
    """Cue Class
    This class represents a cue, which has a number/id and a timecode value.

    Attributes:
        number (float): The cue number/id.
        timecode (float): The timecode value of the cue.

    Methods:
        __post_init__():
            Performs post-initialization tasks for the Cue object.

        timecode_str (property):
            Property to get the timecode in hh:mm:ss:ff format.

    """
    number: float   # Cue number/id
    timecode: float     # Timecode value

    def __post_init__(self):
        """
        Performs post-initialization tasks for the object.

        :param self: The instance of the object.
        :return: None
        """
        # Check if the timecode attribute is a string.
        if isinstance(self.timecode, str):
            # If it is, convert it to a float using the timecode_to_float function.
            self.timecode = timecode_to_float(self.timecode, FPS)

    @property
    def timecode_str(self):
        """Property to get the timecode in hh:mm:ss:ff format"""
        return float_to_timecode(self.timecode, FPS)


@dataclass
class EOSCue(Cue):
    """EOSCue Sub-class
    Represents a cue in the EOS lighting control system.

    Attributes:
        parent_cue_list (list): A reference to the parent.
        duration (float): The duration of the cue.
        follow_time (float): The follow/hang duration.
        label (str): The label of the cue.

    Examples:
        >>> eos_cue = EOSCue(cue_list_number=1, duration=2.5, follow_time=0.5, label="Test Cue")
        >>> print(eos_cue.parent_cue_list.number)
        1
        >>> print(eos_cue.duration)
        2.5
        >>> print(eos_cue.follow_time)
        0.5
        >>> print(eos_cue.label)
        'Test Cue'

    """
    parent_cue_list: 'EOSCueList' = None    # Reference to parent cue list
    duration: float = 0.0   # Duration of cue
    follow_time: float = 0.0    # Follow/Hang duration
    label: str = ""     # Cue label


@dataclass
class EOSCueList:
    number: int = 1     # Cue list number
    cue_list: List['EOSCue'] = field(default_factory=list)  # Contains cues in the cue list


@dataclass
class QLabCue(Cue):
    """QLabCue Sub-class
    Represents a cue in the QLab system. It provides properties and
    methods for managing cues, including cue type, child cues, parent cue,
    * duration, pre-wait time, and post-wait time.

    Attributes:
        cue_type (str): The type of the cue.
        cue_list (List[QLabCue]): A list of child cues, if available.
        parent_cue (Optional[QLabCue]): A reference to the parent cue, if any.
        duration (float): The duration of the cue.
        pre_wait_time (float): The pre-wait time before the cue starts.
        post_wait_time (float): The post-wait time after the cue ends.

    Example usage:
        >>> cue = QLabCue()
        >>> cue.cue_type = "Audio"
        >>> cue.duration = 5.0

        >>> child_cue1 = QLabCue(cue_type="Light")
        >>> child_cue2 = QLabCue(cue_type="Video")
        >>> cue.cue_list = [child_cue1, child_cue2]

        >>> cue.parent_cue = None
        >>> cue.pre_wait_time = 2.0
        >>> cue.post_wait_time = 1.0

    Note:
        This class does not provide specific implementation details, but serves as a blueprint for creating and
        managing cues in the QLab system.

    """
    cue_type: str = ""  # Cue type
    cue_list: List['QLabCue'] = field(default_factory=list) # Contains child cues, if a list
    parent_cue: Optional['QLabCue'] = None  # Reference to parent cue, if any
    duration: float = 0.0   # Duration of cue
    pre_wait_time: float = 0.0  # Pre-wait time
    post_wait_time: float = 0.0 # Post-wait time


class CueManager:
    def __init__(self):
        self.qlab_cues = []
        self.eos_cue_lists = []

    def add_qlab_cue(self, new_cue: QLabCue, cue_list: QLabCue):
        if not isinstance(new_cue, QLabCue):
            raise TypeError(f"Cue {new_cue} must be a QLabCue!")
        if not isinstance(cue_list, QLabCue):
            raise TypeError(f"Cue list {cue_list} must be a QLabCueList!")
        cue_list.cue_list.append(new_cue)

    def add_eos_cue(self, new_cue: EOSCue, cue_list: EOSCueList):
        if not isinstance(new_cue, EOSCue):
            raise TypeError(f"Cue {new_cue} must be a EOSCue!")
        if not isinstance(cue_list, EOSCueList):
            raise TypeError(f"Cue list {cue_list} must be an EOSCueList!")
        cue_list.cue_list.append(new_cue)
