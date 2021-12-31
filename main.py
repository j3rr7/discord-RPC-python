import os
import json
import asyncio
import threading
from math import floor
import time
from pypresence import Presence
import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo

SAVE_FILENAME = "profile.json"

class DiscordRPCGUI:
    __status_online__ = False

    def as_dict(self):
        return {
            "CLIENT_ID": self.CLIENT_ID,
            "instance": self.instance,
            "spectateSecret": self.spectateSecret,
            "joinSecret": self.joinSecret,
            "matchSecret": self.matchSecret,
            "partyMax": self.partyMax,
            "partySize": self.partySize,
            "partyId": self.partyId,
            "smallImageText": self.smallImageText,
            "smallImageKey": self.smallImageKey,
            "largeImageText": self.largeImageText,
            "largeImageKey": self.largeImageKey,
            "endTimestamp": self.endTimestamp,
            "startTimestamp": self.startTimestamp,
            "details": self.details,
            "state": self.state
        }

    def __init__(self):
        self.CLIENT_ID = None
        self.instance = None
        self.spectateSecret = None
        self.joinSecret = None
        self.matchSecret = None
        self.partyMax = None
        self.partySize = None
        self.partyId = None
        self.smallImageText = None
        self.smallImageKey = None
        self.largeImageText = None
        self.largeImageKey = None
        self.endTimestamp = None
        self.startTimestamp = None
        self.details = None
        self.state = None

        self.isrunning = False

        self.load()

        self.__internal_prerender__()
        self.__internal_mainrender__()
        self.__internal_postrender__()

    def __internal_prerender__(self):
        dpg.create_context()
        dpg.create_viewport(
            title="Discord RPC",
            width=800,
            height=600,
            max_width=850,
            max_height=650,
            resizable=False,
            clear_color=(0.14, 0.1, 0, 0.75)
        )
        dpg.setup_dearpygui()

    def __internal_postrender__(self):
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()

    def __internal_mainrender__(self):
        # show_demo()
        with dpg.window(tag="main_window"):
            with dpg.menu_bar(label="Menu Bar"):
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Save")
                    dpg.add_menu_item(label="Save As")
                    dpg.add_menu_item(label="Load")

            dpg.add_text("Discord Custom RPC", pos=((dpg.get_viewport_width() // 2) - 80, 30))
            with dpg.group(pos=((dpg.get_viewport_width() // 2) - 84, 60)):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Start RPC", callback=self.startRPC)
                    dpg.add_button(label="Shutdown RPC", callback=self.stopRPC)

            with dpg.window(label="No CLient ID found", modal=True, show=False, id="modal_error", no_title_bar=True,
                            pos=((dpg.get_viewport_width() // 2) - 100, (dpg.get_viewport_height() // 2) - 50), min_size=(100, 60)):
                dpg.add_text("Please Input Client ID!")
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=30)
                    dpg.add_button(label="OK", width=75, callback=lambda: dpg.configure_item("modal_error", show=False))

            with dpg.child_window(tag="showcase_window", border=True, width=250, height=150,
                                  pos=(10, 20)):
                with dpg.group(pos=(30, 4)):
                    dpg.add_text("Playing a game")
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="img", width=90, height=90)
                        with dpg.group(horizontal=False):
                            dpg.add_text("Game Name", tag="text_state")
                            dpg.add_text("Game Status", tag="text_details")
                            dpg.add_text("Game Party", tag="text_party")
                            dpg.add_text("Elapsed Time", tag="text_time")
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Button 1", width=90, height=20)
                        dpg.add_button(label="Button 2", width=90, height=20)

            with dpg.group(pos=(10, 180)):
                dpg.add_text("Mode Offline", tag="status_text_offline", color=(255, 0, 0, 255), show=False)
                dpg.add_text("Mode Online", tag="status_text_online", color=(0, 255, 255, 255), show=False)
                dpg.show_item("status_text_offline")

                with dpg.group(horizontal=True):
                    dpg.add_input_text(tag="client_id", hint="Client ID", callback=self.__callback_rpc_clientid__)
                    dpg.add_button(label="Set Client ID", enabled=False, arrow=True)

                with dpg.group(pos=(10, 240)):
                    with dpg.group(horizontal=True, horizontal_spacing=50):
                        with dpg.group():
                            dpg.add_input_text(label="state", tag="rpc_state", hint="Looking to Play", width=200,
                                               height=100, callback=self.__callback_rpc_state__)
                            dpg.add_input_text(label="details", tag="rpc_details", hint="In Queue", width=200,
                                               height=100, callback=self.__callback_rpc_details__)

                            dpg.add_spacer(height=20)

                        with dpg.group():
                            with dpg.group(horizontal=True):
                                dpg.add_input_text(label="startTimestamp", tag="rpc_start", hint="1640921000",
                                                   width=200, height=100)
                                dpg.add_button(label="Current",
                                               callback=lambda: dpg.set_value("rpc_start", floor(time.time())))
                            with dpg.group(horizontal=True):
                                dpg.add_input_text(label="endTimestamp", tag="rpc_end", hint="1640921000", width=200,
                                                   height=100)
                                dpg.add_button(label="Current",
                                               callback=lambda: dpg.set_value("rpc_end", floor(time.time())))

                    with dpg.group(horizontal=True, horizontal_spacing=50):
                        with dpg.group():
                            dpg.add_input_text(label="largeImageKey", tag="rpc_image_large", hint="default", width=200,
                                               height=100)
                            dpg.add_input_text(label="largeImageText", tag="rpc_image_large_text", width=200,
                                               hint="Danger Zone")
                            dpg.add_input_text(label="smallImageKey", tag="rpc_image_small", hint="rogue", width=200,
                                               height=100)
                            dpg.add_input_text(label="smallImageText", tag="rpc_image_small_text", width=200,
                                               hint="Rogue - Level 100")
                            dpg.add_spacer(height=10)
                            with dpg.group(horizontal=True):
                                dpg.add_checkbox(label="Button 1")
                                dpg.add_checkbox(label="Button 2")

                            dpg.add_input_text(label="Button 1 Text", hint="Play", width=200)
                            dpg.add_input_text(label="Button 2 Text", hint="Spectate",width=200)
                        with dpg.group():
                            dpg.add_input_text(label="partyId", tag="rpc_party_id",
                                               hint="ae488379-351d-4a4f-ad32-2b9b01c91657", width=300)
                            dpg.add_input_int(label="partySize", tag="rpc_party_size", width=300)
                            dpg.add_input_int(label="partyMax", tag="rpc_party_max", width=300)
                            dpg.add_input_text(label="matchSecret", tag="rpc_match_secret",
                                               hint="MmhuZToxMjMxMjM6cWl3amR3MWlqZA==", width=300)
                            dpg.add_input_text(label="spectateSecret", tag="rpc_spectate_secret",
                                               hint="MTIzNDV8MTIzNDV8MTMyNDU0", width=300)
                            dpg.add_input_text(label="joinSecret", tag="rpc_join_secret",
                                               hint="MTI4NzM0OjFpMmhuZToxMjMxMjM=", width=300)
                            dpg.add_checkbox(label="instance", tag="rpc_instance", callback=self.__callback_rpc_instance__)

    def __callback_rpc_state__(self, appid):
        self.state = dpg.get_value(appid)
        if self.state is None or self.state != "":
            dpg.set_value("text_state", self.state)
        else:
            dpg.set_value("text_state", "Game Name")

    def __callback_rpc_details__(self, appid):
        self.details = dpg.get_value(appid)
        if self.details is None or self.details != "":
            dpg.set_value("text_details", self.details)
        else:
            dpg.set_value("text_details", "Game Status")

    def __callback_rpc_instance__(self, appid):
        self.instance = dpg.get_value(appid)
        print(f"Instance: {self.instance}")

    def __callback_rpc_clientid__(self, appid, userdata):
        self.CLIENT_ID = dpg.get_value(appid)

    def startRPC(self, appid):
        if self.CLIENT_ID is None or self.CLIENT_ID == "":
            dpg.configure_item("modal_error", show=True)
            return

        dpg.show_item("status_text_online")
        dpg.hide_item("status_text_offline")

        # using asyncio to run a thread
        # https://docs.python.org/3/library/asyncio-task.html
        self.loop = asyncio.run(self.presence_update())

    async def presence_update(self):
        precence = Presence(self.CLIENT_ID)
        print("Connecting...")
        precence.connect()
        print("Connected!")
        precence.update(
            state=self.state if self.state is not None and self.state != "" else None,
            details=self.details if self.details is not None and self.details != "" else None,
            start=self.startTimestamp if self.startTimestamp != 0 else None,
            end=self.endTimestamp if self.endTimestamp != 0 else None,
            large_image=self.largeImageKey if self.largeImageKey != "" else None,
            large_text=self.largeImageText if self.largeImageText != "" else None,
            small_image=self.smallImageKey if self.smallImageKey != "" else None,
            small_text=self.smallImageText if self.smallImageText != "" else None,
            party_id=self.partyId if self.partyId != "" else None,
            party_size=[self.partySize if self.partySize != 0 else None,
                        self.partyMax if self.partyMax != 0 else None] if not [None, None] else None,
            join=self.joinSecret if self.joinSecret != "" else None,
            spectate=self.spectateSecret if self.spectateSecret != "" else None,
            match=self.matchSecret if self.matchSecret != "" else None,
            buttons=[{"label": "a", "url": "https//discord.gg/"}, {"label": "b", "url": "https//discord.gg/"}],
            instance=self.instance if self.instance is True else None
        )
        while True:
            await asyncio.sleep(5)

    def stopRPC(self):
        if self.loop is not None:
            self.loop.stop()

        dpg.hide_item("status_text_online")
        dpg.show_item("status_text_offline")

    def save(self):
        with open(SAVE_FILENAME, "w") as f:
            f.write(json.dumps(self.as_dict(), indent=4))

    def load(self):
        if os.path.isfile(SAVE_FILENAME):
            with open(SAVE_FILENAME, "r") as f:
                self.__dict__ = json.loads(f.read())
        else:
            self.save()


if __name__ == '__main__':
    rpc = DiscordRPCGUI()
    rpc.save()
