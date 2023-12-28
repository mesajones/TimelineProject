"""Defines the OSC handler class."""

import asyncio
from asyncio import Task
from typing import Tuple, Optional, Any

from pythonosctcp import Dispatcher, AsyncTCPClient

from config.settings import SERVER_ADDRESS


class OSCHandler:
    def __init__(self, loop, gui):
        self.dispatcher = Dispatcher()
        self.client = AsyncTCPClient(server_address=SERVER_ADDRESS, dispatcher=self.dispatcher)
        self.loop = loop
        self.gui = gui

        asyncio.run_coroutine_threadsafe(self.run(), self.loop)

    async def run(self):
        client_task = await start_client(self.client, self.gui)

    def send_message(self, address, *args):
        asyncio.run_coroutine_threadsafe(self.client.add_message(address, *args), self.loop)


async def start_client(
        client: AsyncTCPClient,
        gui: Any,
        server_address: Tuple[str, int] = SERVER_ADDRESS) -> Optional[Task]:
    """Starts the AsyncTCPClient and returns an AsyncIO Task object"""
    try:
        client_task = asyncio.create_task(client.run())

        # Wait for a short period to allow connection to establish
        await asyncio.sleep(1)

        if client.is_connected():
            print(f"Client successfully connected to address {server_address}")
            return client_task
        else:
            raise ConnectionError(f"Error while connecting to {server_address}")

    except (OSError, ConnectionRefusedError, ConnectionError) as e:
        print(e)
        print("Please try a different address/port.")
        new_address_future = gui.network_error_prompt(server_address)
        new_address = await new_address_future
        if new_address[0] is not None or new_address[1] is not None:
            server_address = new_address
            client.alter_server_address(server_address)
            return await start_client(client, gui, server_address)  # Restart the connection process
        else:
            return None

    except Exception as e:
        print(f"An error occurred: {e}", True)
        raise
