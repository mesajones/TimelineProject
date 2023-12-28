"""Defines the OSC handler class."""

import asyncio
from asyncio import Task
from typing import Tuple, Optional, Any

from pythonosctcp import Dispatcher, AsyncTCPClient

from utils import parse_json
from config.settings import QLAB_ADDRESS, EOS_ADDRESS


class OSCHandler:
    def __init__(self, loop, gui):
        self.qlab_dispatcher = Dispatcher()
        self.qlab_client = AsyncTCPClient(server_address=QLAB_ADDRESS, dispatcher=self.qlab_dispatcher)
        self.qlab_connected = False
        self.eos_dispatcher = Dispatcher()
        self.eos_client = AsyncTCPClient(server_address=EOS_ADDRESS, dispatcher=self.eos_dispatcher)
        self.eos_connected = False
        self.loop = loop
        self.gui = gui

        asyncio.run_coroutine_threadsafe(self.run(), self.loop)

    async def run(self):
        try:
            qlab_client_task = await start_client(self.qlab_client, self.gui, QLAB_ADDRESS)
            eos_client_task = await start_client(self.eos_client, self.gui, EOS_ADDRESS)
            self.qlab_connected = await self.connect_to_qlab()
            if self.qlab_connected is None:
                raise ConnectionError("Failed to connect to QLab!")
        except ConnectionError as e:
            print(e)
            raise
        except asyncio.CancelledError:
            return

    @staticmethod
    async def query_and_wait(
            client: AsyncTCPClient, dispatcher: Dispatcher,
            query_address: str, response_address: str, *args: Tuple[Any, ...],
            check_interval=0.1, timeout=5.0):
        # Define the start time for the timeout
        start_time = asyncio.get_event_loop().time()

        # Wait until no handler is mapped to the response_address
        while dispatcher.handlers.get(response_address):
            await asyncio.sleep(check_interval)
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for handler to be free.")

        response_future = asyncio.Future()

        # Define a response handler
        async def response_handler(*response_args):
            if not response_future.done():
                response_future.set_result(response_args)

        # Set the handler for the expected response
        dispatcher.map(response_address, response_handler)

        # Send the query
        await client.add_message(query_address, *args)

        try:
            # Wait for the response
            response = await response_future
            return response
        except asyncio.CancelledError:
            # Handle cancellation of the query
            raise
        except Exception as e:
            # Handle other exceptions and reflect them in the future
            if not response_future.done():
                response_future.set_exception(e)
            raise
        finally:
            # Clean up by unmapping the handler
            if dispatcher.handlers.get(response_address):
                dispatcher.unmap(response_address)

    async def connect_to_qlab(self):
        if self.qlab_connected:
            raise ConnectionError("QLab already connected")
        response_json = await self.query_and_wait(
            self.qlab_client, self.qlab_dispatcher,
            query_address="/workspaces", response_address="/reply/workspaces",
        )
        response = parse_json(response_json)
        if response is None or response['status'] == 'error':
            raise ConnectionError("Error whilst connecting to QLab.")
        if response['status'] == 'ok':
            workspace_uid = response['data']['uniqueID']
            connect_response_json = await self.query_and_wait(
                self.qlab_client, self.qlab_dispatcher,
                query_address=f"/workspace/{workspace_uid}/connect",
                response_address=f"/reply/workspace/{workspace_uid}/connect",
            )
            connect_response = parse_json(connect_response_json)
            if connect_response is None or connect_response['status'] == 'error':
                raise ConnectionError(f"Error whilst connecting to QLab workspace {workspace_uid}.")
            if response['status'] == 'ok' and response['data'] == 'ok':
                return True
        return None


async def start_client(
        client: AsyncTCPClient,
        gui: Any,
        server_address: Tuple[str, int]) -> Optional[Task]:
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
