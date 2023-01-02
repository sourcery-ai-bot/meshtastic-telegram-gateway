import logging
import sys
import time
#
from typing import (
    Dict,
    List,
)
#
from meshtastic import (
    LOCAL_ADDR as MESHTASTIC_LOCAL_ADDR,
    serial_interface as meshtastic_serial_interface,
    tcp_interface as meshtastic_tcp_interface,
)


class MeshtasticConnection:
    """
    Meshtastic device connection
    """

    def __init__(self, dev_path: str, logger: logging.Logger, startup_ts = time.time()):
        self.dev_path = dev_path
        self.interface = None
        self.logger = logger
        self.startup_ts = startup_ts

    @property
    def get_startup_ts(self):
        """
        get_startup_ts - returns Unix timestamp since startup
        """
        return self.startup_ts

    def connect(self):
        """
        Connect to Meshtastic device. Interface can be later updated during reboot procedure

        :return:
        """
        if not self.dev_path.startswith('tcp:'):
            self.interface = meshtastic_serial_interface.SerialInterface(devPath=self.dev_path, debugOut=sys.stdout)
        else:
            self.interface = meshtastic_tcp_interface.TCPInterface(self.dev_path.lstrip('tcp:'), debugOut=sys.stdout)

    def send_text(self, *args, **kwargs) -> None:
        """
        Send Meshtastic message

        :param args:
        :param kwargs:
        :return:
        """
        self.interface.sendText(*args, **kwargs)

    def node_info(self, node_id) -> Dict:
        """
        Return node information for a specific node ID

        :param node_id:
        :return:
        """
        return self.interface.nodes.get(node_id, {})

    def reboot(self):
        """
        Execute Meshtastic device reboot

        :return:
        """
        self.logger.info("Reboot requested...")
        self.interface.getNode(MESHTASTIC_LOCAL_ADDR).reboot(10)
        self.interface.close()
        time.sleep(20)
        self.connect()
        self.logger.info("Reboot completed...")

    @property
    def nodes(self) -> Dict:
        """
        Return dictionary of nodes

        :return:
        """
        return self.interface.nodes if self.interface.nodes else {}

    @property
    def nodes_with_info(self) -> List:
        """
        Return list of nodes with information

        :return:
        """
        node_list = []
        for node in self.nodes:
            node_list.append(self.nodes.get(node))
        return node_list

    @property
    def nodes_with_position(self) -> List:
        """
        Filter out nodes without position

        :return:
        """
        node_list = []
        for node_info in self.nodes_with_info:
            if not node_info.get('position'):
                continue
            node_list.append(node_info)
        return node_list

    @property
    def nodes_with_user(self) -> List:
        """
        Filter out nodes without position or user

        :return:
        """
        node_list = []
        for node_info in self.nodes_with_position:
            if not node_info.get('user'):
                continue
            node_list.append(node_info)
        return node_list
