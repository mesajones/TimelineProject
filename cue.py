import asyncio
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple

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
    uid: str = ''           # Cue UID
    number: float = 0.0     # Cue number
    timecode: Optional[float, None] = 0.0   # Timecode value
    label: str = ""  # Cue label

    def __post_init__(self):
        """
        Performs post-initialization tasks for the object.

        :param self: The instance of the object.
        :return: None
        """
        # Check if the timecode attribute is a string.
        if isinstance(self.timecode, str):
            # If it is, convert it to a float using the timecode_to_float function.
            if len(self.timecode) == 11:
                self.timecode = timecode_to_float(self.timecode)
            else:
                self.timecode = None

    @property
    def timecode_str(self):
        """Property to get the timecode in hh:mm:ss:ff format"""
        if self.timecode:
            return float_to_timecode(self.timecode)
        else:
            return None


@dataclass
class EOSCue(Cue):
    """EOSCue Sub-class
    Represents a cue in the EOS lighting control system.

    !!! NOTE: EXECUTIVE DECISION MADE TO REMOVE DURATIONS FROM EOS CUE CLASS !!!

    Attributes:
        parent_cue_list (list): A reference to the parent.
        # duration (float): The duration of the cue.
        # follow_time (float): The follow/hang duration.
        label (str): The label of the cue.

    Examples:
        >>> eos_cue = EOSCue(cue_list_number=1, label="Test Cue") #, duration=2.5, follow_time=0.5)
        >>> print(eos_cue.parent_cue_list.number)
        1
        # >>> print(eos_cue.duration)
        2.5
        # >>> print(eos_cue.follow_time)
        0.5

    """
    parent_cue_list: 'EOSCueList' = None    # Reference to parent cue list
    # duration: float = 0.0   # Duration of cue
    # follow_time: float = 0.0    # Follow/Hang duration


@dataclass
class EOSCueList:
    """ EOSCueList Class
    Represents a cue list in the EOS lighting control system.

    Attributes:
        number (int): The number of the cue list.
        cue_list_dict (Dict['EOSCue']): The list of cues in the cue list.
    """
    uid: str = ''   # Cue list unique ID
    number: int = 1     # Cue list number
    cue_list_dict: Dict[str: 'EOSCue'] = field(default_factory=dict)  # Contains cues in the cue list


@dataclass
class QLabCue(Cue):
    """QLabCue Sub-class
    Represents a cue in the QLab system. It provides properties and
    methods for managing cues, including cue type, child cues, parent cue,
    * duration, pre-wait time, and post-wait time.

    Attributes:
        type (str): The type of the cue.
        cue_list (List[QLabCue]): A list of child cues, if available.
        parent_cue (Optional[QLabCue]): A reference to the parent cue, if any.
        duration (float): The duration of the cue.
        pre_wait_time (float): The pre-wait time before the cue starts.
        post_wait_time (float): The post-wait time after the cue ends.
        file_target_path (str): The file target of the

    Example usage:
        >>> cue = QLabCue()
        >>> cue.type = "Audio"
        >>> cue.duration = 5.0

        >>> child_cue1 = QLabCue(type="Light")
        >>> child_cue2 = QLabCue(type="Video")
        >>> cue.cue_list = [child_cue1, child_cue2]

        >>> cue.parent_cue = None
        >>> cue.pre_wait_time = 2.0
        >>> cue.post_wait_time = 1.0

    Note:
        This class does not provide specific implementation details, but serves as a blueprint for creating and
        managing cues in the QLab system.

    """
    type: str = ""  # Cue type
    cue_dict: Dict[str: 'QLabCue'] = field(default_factory=dict)     # Contains child cues, if a list
    parent_cue: Optional['QLabCue'] = None  # Reference to parent cue, if any
    duration: float = 0.0   # Duration of cue
    pre_wait_time: float = 0.0      # Pre-wait time
    post_wait_time: float = 0.0     # Post-wait time
    file_target_path: Optional[str] = None  # File target path
    target_id: Optional[str] = None     # Target cue ID

    def __post_init__(self):
        super().__post_init__()
        if isinstance(self.duration, str):
            self.duration = float(self.duration)
        if isinstance(self.pre_wait_time, str):
            self.pre_wait_time = float(self.duration)
        if isinstance(self.post_wait_time, str):
            self.post_wait_time = float(self.duration)


class CueManager:
    """
    CueManager

    The CueManager class is responsible for managing cues in QLab and EOS. It provides methods to add, remove, and
    retrieve cues from both systems.

    Attributes:
        loop (asyncio.BaseEventLoop): The event loop used for asynchronous operations.
        osc_handler (OscHandler): The OSC handler used to communicate with QLab and EOS.
        qlab_cues (dict): A dictionary containing QLab cue objects.
        eos_cues (dict): A dictionary containing EOS cue and cue list objects.

    Methods:
        __init__(loop, osc_handler)
            Initializes a new instance of the CueManager class.

        add_qlab_cue(new_cue, parent_cue_id=None)
            Adds a new QLab cue to the cue manager.

            Parameters:
                new_cue (QLabCue): The new QLab cue to add.
                parent_cue_id (str): The ID of the parent cue if this cue is nested.

        remove_qlab_cue(cue_id)
            Removes the specified QLab cue from the cue manager.

            Parameters:
                cue_id (str): The ID of the QLab cue to remove.

        solve_nested_qlab_cues(parent_cue, cue_data)
            Solves the nested QLab cues and adds them to the cue manager.

            Parameters:
                parent_cue (QLabCue): The parent cue to add the nested cues to.
                cue_data (List[Dict[str, Any]]): The list of nested cues data.

        add_extra_qlab_data()
            Adds extra data (duration, pre wait time, post wait time, and timecode trigger) to QLab cues.

        populate_qlab_cue_dict()
            Populates the QLab cue dictionary by querying the QLab server.

        add_eos_cue(new_cue, parent_cue_id=None)
            Adds a new EOS cue to the cue manager.

            Parameters:
                new_cue (EOSCue): The new EOS cue to add.
                parent_cue_id (str): The ID of the parent cue list if this cue is nested.

        remove_eos_cue(cue_id)
            Removes the specified EOS cue from the cue manager.

            Parameters:
                cue_id (str): The ID of the EOS cue to remove.

        populate_eos_cue_dict()
            Populates the EOS cue dictionary by querying the EOS server.

        query(client, dispatcher, query, response)
            Executes an OSC query and waits for the response.

            Parameters:
                client (OscClient): The OSC client to send the query to.
                dispatcher (OscDispatcher): The OSC dispatcher to handle the response.
                query (str): The OSC query message.
                response (str): The OSC response address.
    """
    def __init__(self, loop, osc_handler):
        self.loop = loop
        self.osc_handler = osc_handler

        self.qlab_cues = {}
        self.eos_cues = {}

    async def initialise(self):
        self.loop.create_task(self.populate_qlab_cue_dict())
        self.loop.create_task(self.populate_eos_cue_dict())

    # QLAB
    async def add_qlab_cue(self, new_cue: QLabCue, parent_cue_id: Optional[str] = None):
        if parent_cue_id:
            parent_cue = self.qlab_cues.get(parent_cue_id)
            if parent_cue:
                parent_cue.cue_dict[new_cue.uid] = new_cue
                if new_cue.parent_cue != parent_cue:
                    new_cue.parent_cue = parent_cue
            else:
                raise ValueError(f"Parent QLabCue with ID {parent_cue_id} not found.")
        self.qlab_cues[new_cue.uid] = new_cue

    async def remove_qlab_cue(self, cue_id: str):
        cue = self.qlab_cues.pop(cue_id, None)
        if cue:
            if cue.parent_cue:
                del cue.parent_cue.cue_dict[cue_id]
            cue.parent_cue = None
        else:
            raise ValueError(f"QLabCue with ID {cue_id} not found.")

    async def solve_nested_qlab_cues(self, parent_cue: QLabCue, cue_data: List[Dict[str, Any]]):
        for c in cue_data:
            qlab_cue = QLabCue(
                uid=c['uniqueID'],
                number=c['number'],
                parent_cue=parent_cue,
                type=c['type'],
                label=c['name']
            )
            parent_cue.cue_dict[qlab_cue.uid] = qlab_cue
            self.qlab_cues[qlab_cue.uid] = qlab_cue

            if 'cues' in c and len(c['cues']) > 0:
                await self.solve_nested_qlab_cues(qlab_cue, c['cues'])

    async def add_extra_qlab_data(self):
        attribute_query_list = ["/duration", "/preWait", "/postWait", "/timecodeTrigger/text"]

        # Iterate over all cues generated.
        for cue_id, cue in self.qlab_cues.items():

            # Handle file target path acquisition
            address, response_json = await self.query(
                client=self.osc_handler.qlab_client,
                dispatcher=self.osc_handler.qlab_dispatcher,
                query=f'/cue_id/{cue_id}/hasFileTargets',
                response=f'/reply/cue_id/{cue_id}/hasFileTargets'
            )
            response = parse_json(response_json)
            if response['data']:    # If hasFileTargets is True, then query the file target and record.
                address, response_json = await self.query(
                    client=self.osc_handler.qlab_client,
                    dispatcher=self.osc_handler.qlab_dispatcher,
                    query=f'/cue_id/{cue_id}/fileTarget',
                    response=f'/reply/cue_id/{cue_id}/fileTarget'
                )
                response = parse_json(response_json)
                cue.file_target_path = response['data']

            # Handle cue target path acquisition
            address, response_json = await self.query(
                client=self.osc_handler.qlab_client,
                dispatcher=self.osc_handler.qlab_dispatcher,
                query=f'/cue_id/{cue_id}/hasCueTargets',
                response=f'/reply/cue_id/{cue_id}/hasCueTargets'
            )
            response = parse_json(response_json)
            if response['data']:  # If hasCueTargets is True, then query the cue target id and record.
                address, response_json = await self.query(
                    client=self.osc_handler.qlab_client,
                    dispatcher=self.osc_handler.qlab_dispatcher,
                    query=f'/cue_id/{cue_id}/cueTargetID',
                    response=f'/reply/cue_id/{cue_id}/cueTargetID'
                )
                response = parse_json(response_json)
                cue.target_id = response['data']

            # Handle all other attributes
            for attribute in attribute_query_list:
                query_address = f"/cue_id/{cue_id}{attribute}"
                response_address = f"/reply/cue_id/{cue_id}{attribute}"
                address, response_json = await self.query(
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

    async def populate_qlab_cue_dict(self):
        self.qlab_cues.clear()
        address, response_json = await self.query(
            client=self.osc_handler.qlab_client,
            dispatcher=self.osc_handler.qlab_dispatcher,
            query='/cueLists', response='/reply/cueLists'
        )
        response = parse_json(response_json)
        if response and response['status'] == 'ok':
            for cue_list_data in response['data']:
                root_cue = QLabCue(
                    uid=cue_list_data['uniqueID'],
                    number=cue_list_data['number'],
                    parent_cue=None,
                    type=cue_list_data['type'],
                    label=cue_list_data['name']
                )
                self.qlab_cues[root_cue.uid] = root_cue
                if 'cues' in cue_list_data and cue_list_data['cues']:
                    await self.solve_nested_qlab_cues(root_cue, cue_list_data['cues'])
            await self.add_extra_qlab_data()

    # EOS
    async def add_eos_cue(self, new_cue: QLabCue, parent_cue_id: Optional[str] = None):
        if parent_cue_id:
            parent_cue_list = self.eos_cues.get(parent_cue_id)
            if parent_cue_list:
                parent_cue_list.cue_dict[new_cue.uid] = new_cue
                if new_cue.parent_cue_list != parent_cue_list:
                    new_cue.parent_cue_list = parent_cue_list
            else:
                raise ValueError(f"Parent EOSCueList with ID {parent_cue_id} not found.")
        self.eos_cues[new_cue.uid] = new_cue

    async def remove_eos_cue(self, cue_id: str):
        cue = self.eos_cues.pop(cue_id, None)
        if cue:
            if cue.parent_cue_list:
                del cue.parent_cue_list.cue_dict[cue_id]
            cue.parent_cue = None
        else:
            raise ValueError(f"EOSCue with ID {cue_id} not found.")

    async def populate_eos_cue_dict(self):
        self.eos_cues.clear()
        address, response = await self.query(
            client=self.osc_handler.eos_client,
            dispatcher=self.osc_handler.eos_dispatcher,
            query='/eos/get/cuelist/count', response='/eos/out/get/cuelist/count'
        )
        cue_list_count = int(response[0])
        for cue_list in range(cue_list_count):
            address, cue_list_data = await self.query(
                    client=self.osc_handler.eos_client,
                    dispatcher=self.osc_handler.eos_dispatcher,
                    query=f'/eos/get/cuelist/index/{cue_list}',
                    response='/eos/out/get/cuelist/*/list/*/*'
                )
            components = address.split('/')
            cue_list_uid = response[1]
            cue_list_number = int(components[6])
            cue_list_obj = EOSCueList(uid=cue_list_uid, number=cue_list_number)
            self.eos_cues[cue_list_obj.uid] = cue_list_obj
            address, response = await self.query(
                    client=self.osc_handler.eos_client,
                    dispatcher=self.osc_handler.eos_dispatcher,
                    query=f'/eos/get/cue/{cue_list_number}/count',
                    response=f'/eos/out/get/cue/{cue_list_number}/count'
                )
            cue_count_in_cue_list = int(response[0])
            for cue in range(cue_count_in_cue_list):
                address, response = await self.query(
                    client=self.osc_handler.eos_client,
                    dispatcher=self.osc_handler.eos_dispatcher,
                    query=f'/eos/get/cue/{cue_list_number}/index/{cue}',
                    response='/eos/out/get/cue/*/*/*/list/*/*'
                )
                components = address.split('/')
                cue_number, part_number = int(components[6]), int(components[7])
                if part_number != 0:
                    continue
                cue_uid, label, timecode = response[1], response[2], response[25]
                if len(timecode) != 11:
                    timecode = ''
                cue_object = EOSCue(uid=cue_uid, parent_cue_list=cue_list_obj, label=label, timecode=timecode)
                cue_list_obj.cue_list_dict[cue_object.uid] = cue_object

    async def query(
            self, client, dispatcher, query, response, *args: Optional[Tuple[Any, ...]]) -> Optional[List[Any, ...]]:
        try:
            return await self.osc_handler.query_and_wait(
                client=client,
                dispatcher=dispatcher,
                query_address=query,
                response_address=response,
                args=args
            )
        except asyncio.TimeoutError:
            print("Query timed out.")
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
