import asyncio
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from utils import timecode_to_float, float_to_timecode, parse_json
from config.settings import TIMECODE_FPS


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
    number: float = 0.0     # Cue number/id
    timecode: float = 0.0   # Timecode value

    def __post_init__(self):
        """
        Performs post-initialization tasks for the object.

        :param self: The instance of the object.
        :return: None
        """
        # Check if the timecode attribute is a string.
        if isinstance(self.timecode, str):
            # If it is, convert it to a float using the timecode_to_float function.
            self.timecode = timecode_to_float(self.timecode, TIMECODE_FPS)

    @property
    def timecode_str(self):
        """Property to get the timecode in hh:mm:ss:ff format"""
        return float_to_timecode(self.timecode, TIMECODE_FPS)


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
    """ EOSCueList Class
    Represents a cue list in the EOS lighting control system.

    Attributes:
        number (int): The number of the cue list.
        cue_list (List[EOSCue]): The list of cues in the cue list.
    """
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
    cue_label: str = ""     # Cue label
    cue_type: str = ""  # Cue type
    cue_list: List['QLabCue'] = field(default_factory=list) # Contains child cues, if a list
    parent_cue: Optional['QLabCue'] = None  # Reference to parent cue, if any
    duration: float = 0.0   # Duration of cue
    pre_wait_time: float = 0.0  # Pre-wait time
    post_wait_time: float = 0.0 # Post-wait time

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.duration, str):
            self.duration = float(self.duration)
        if isinstance(self.pre_wait_time, str):
            self.pre_wait_time = float(self.duration)
        if isinstance(self.post_wait_time, str):
            self.post_wait_time = float(self.duration)


class CueManager:
    def __init__(self, loop, osc_handler):
        self.loop = loop
        self.osc_handler = osc_handler

        self.qlab_cues = {}
        self.eos_cue_lists = {}

    async def add_qlab_cue(self, new_cue: QLabCue, parent_cue_id: str):
        parent_cue = self.qlab_cues.get(parent_cue_id)
        if parent_cue:
            parent_cue.cue_list.append(new_cue)
            new_cue.parent_cue = parent_cue
            self.qlab_cues[new_cue.unique_id] = new_cue
        else:
            raise ValueError(f"Parent QLabCue with ID {parent_cue_id} not found.")

    async def remove_qlab_cue(self, cue_id: str):
        cue = self.qlab_cues.pop(cue_id, None)
        if cue:
            if cue.parent_cue:
                cue.parent_cue.cue_list.remove(cue)
            cue.parent_cue = None
        else:
            raise ValueError(f"QLabCue with ID {cue_id} not found.")

    async def solve_nested_qlab_cues(self, parent_cue: QLabCue, cue_data: List[Dict[str, Any]]):
        for c in cue_data:
            qlab_cue = QLabCue(
                number=c['number'],
                parent_cue=parent_cue,
                cue_type=c['type'],
                cue_label=c['name']
            )
            parent_cue.cue_list.append(qlab_cue)
            self.qlab_cues[qlab_cue.unique_id] = qlab_cue

            if 'cues' in c and len(c['cues']) > 0:
                await self.solve_nested_qlab_cues(qlab_cue, c['cues'])

    async def populate_qlab_cues_dict(self):
        self.qlab_cues.clear()
        response_json = await self.query(
            client=self.osc_handler.qlab_client,
            dispatcher=self.osc_handler.qlab_dispatcher,
            query='/cueLists', response='/reply/cueLists'
        )
        if response_json and response_json['status'] == 'ok':
            for cue_list_data in response_json['data']:
                root_cue = QLabCue(
                    number=cue_list_data['number'],
                    parent_cue=None,
                    cue_type=cue_list_data['type'],
                    cue_label=cue_list_data['name']
                )
                self.qlab_cues[root_cue.unique_id] = root_cue
                if 'cues' in cue_list_data and cue_list_data['cues']:
                    await self.solve_nested_qlab_cues(root_cue, cue_list_data['cues'])

    async def add_extra_data(self):
        attribute_query_list = ["/duration", "/preWait", "/postWait", "/timecodeTrigger/text"]
        for cue_id, cue in self.qlab_cues.items():
            for attribute in attribute_query_list:
                query_address = f"/cue_id/{cue_id}{attribute}"
                response_address = f"/reply/cue_id/{cue_id}{attribute}"
                response_json = await self.query(
                    client=self.osc_handler.qlab_client,
                    dispatcher=self.osc_handler.qlab_dispatcher,
                    query=query_address,
                    response=response_address
                )
                response = parse_json(response_json)
                if attribute == '/duration':
                    cue.duration = response['data']
                elif attribute == '/preWait':
                    cue.pre_wait_time = response['data']
                elif attribute == '/postWait':
                    cue.pre_wait_time = response['data']
                elif attribute == '/timecodeTrigger/text':
                    cue.timecode = response['data']

    async def query(self, client, dispatcher, query, response):
        try:
            return await self.osc_handler.query_and_wait(
                client=client,
                dispatcher=dispatcher,
                query_address=query,
                response_address=response
            )
        except asyncio.TimeoutError:
            print("Query timed out.")
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
