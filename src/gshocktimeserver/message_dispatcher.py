import asyncio
import json
from typing import Any
import connection
from casio_constants import CasioConstants
from utils import to_compact_string, to_hex_string, to_int_array
from alarms import alarms_inst, alarm_decoder

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class AlarmsIO:
    @staticmethod
    async def send_to_watch(message):
        alarm_command = to_compact_string(
            to_hex_string(bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]]))
        )
        await connection.write(0x000C, alarm_command)

    @staticmethod
    async def send_to_watch_set(message):
        alarms_json_arr = json.loads(message).get("value")
        alarm_casio0 = to_compact_string(
            to_hex_string(alarms_inst.from_json_alarm_first_alarm(alarms_json_arr[0]))
        )
        await connection.write(0x000E, alarm_casio0)
        alarm_casio = to_compact_string(
            to_hex_string(alarms_inst.from_json_alarm_secondary_alarms(alarms_json_arr))
        )
        await connection.write(0x000E, alarm_casio)

    @staticmethod
    def on_received(message):
        print(f"AlarmsIO onReceived: {message}")


class EventsIO:
    @staticmethod
    def send_to_watch_set(message):
        print(f"EventsIO sendToWatchSet: {message}")

    @staticmethod
    def on_received(message):
        print(f"EventsIO onReceived: {message}")

    @staticmethod
    def on_received_title(message):
        print(f"EventsIO onReceivedTitle: {message}")


class SettingsIO:
    @staticmethod
    def send_to_watch(message):
        print(f"SettingsIO sendToWatch: {message}")

    @staticmethod
    def send_to_watch_set(message):
        print(f"SettingsIO sendToWatchSet: {message}")

    @staticmethod
    def on_received(message):
        print(f"SettingsIO onReceived: {message}")


class TimeAdjustmentIO:
    @staticmethod
    def send_to_watch(message):
        print(f"TimeAdjustmentIO sendToWatch: {message}")

    @staticmethod
    def send_to_watch_set(message):
        print(f"TimeAdjustmentIO sendToWatchSet: {message}")

    @staticmethod
    def on_received(message):
        print(f"TimeAdjustmentIO onReceived: {message}")


class TimerIO:
    result: asyncio.Future[Any] = None

    @staticmethod
    async def request(connection):
        print(f"TimerIO request")
        await connection.request("18")

        loop = asyncio.get_running_loop()
        TimerIO.result = loop.create_future()
        return TimerIO.result

    @staticmethod
    async def send_to_watch(message):
        print(f"TimerIO sendToWatch: {message}")
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_TIMER"]]))

    @staticmethod
    async def send_to_watch_set(data):
        print(f"TimerIO sendToWatchSet: {data}")

        def encode(seconds_str):
            in_seconds = int(seconds_str)
            hours = in_seconds // 3600
            minutes_and_seconds = in_seconds % 3600
            minutes = minutes_and_seconds // 60
            seconds = minutes_and_seconds % 60

            arr = bytearray(7)
            arr[0] = 0x18
            arr[1] = hours
            arr[2] = minutes
            arr[3] = seconds
            return arr

        seconds_as_byte_arr = encode(seconds)
        seconds_as_compact_str = to_compact_string(to_hex_string(seconds_as_byte_arr))
        await connection.write(0x000E, seconds_as_compact_str)

    @staticmethod
    def on_received(data):
        print(f"TimerIO onReceived: {data}")

        def decode_value(data: str) -> str:
            timer_int_array = data

            hours = timer_int_array[1]
            minutes = timer_int_array[2]
            seconds = timer_int_array[3]

            in_seconds = hours * 3600 + minutes * 60 + seconds
            return in_seconds

        decoded = decode_value(data)
        seconds = int(decoded)
        TimerIO.result.set_result(seconds)


class TimeIO:
    @staticmethod
    def send_to_watch_set(message):
        print(f"TimeIO sendToWatchSet: {message}")

    @staticmethod
    def on_received(message):
        print(f"TimeIO onReceived: {message}")


class WatchNameIO:
    result: asyncio.Future[Any] = None

    @staticmethod
    def on_received(self, data):
        print(f"WatchNameIO onReceived: {data}")

    @staticmethod
    async def request(self):
        print(f"WatchNameIO request: {self}")


class DstForWorldCitiesIO:
    @staticmethod
    def on_received(message):
        print(f"DstForWorldCitiesIO onReceived: {message}")


class WorldCitiesIO:
    @staticmethod
    def on_received(message):
        print(f"WorldCitiesIO onReceived: {message}")


class DstWatchStateIO:
    @staticmethod
    def on_received(message):
        print(f"DstWatchStateIO onReceived: {message}")


class WatchConditionIO:
    @staticmethod
    def on_received(message):
        print(f"WatchConditionIO onReceived: {message}")


class AppInfoIO:
    @staticmethod
    def on_received(message):
        print(f"AppInfoIO onReceived: {message}")


class ButtonPressedIO:
    @staticmethod
    def on_received(message):
        print(f"ButtonPressedIO onReceived: {message}")


class ErrorIO:
    @staticmethod
    def on_received(message):
        print(f"ErrorIO onReceived: {message}")


class UnknownIO:
    @staticmethod
    def on_received(message):
        print(f"UnknownIO onReceived: {message}")


class MessageDispatcher:
    watch_senders = {
        "GET_ALARMS": AlarmsIO.send_to_watch,
        "SET_ALARMS": AlarmsIO.send_to_watch_set,
        "SET_REMINDERS": EventsIO.send_to_watch_set,
        "GET_SETTINGS": SettingsIO.send_to_watch,
        "SET_SETTINGS": SettingsIO.send_to_watch_set,
        "GET_TIME_ADJUSTMENT": TimeAdjustmentIO.send_to_watch,
        "SET_TIME_ADJUSTMENT": TimeAdjustmentIO.send_to_watch_set,
        "GET_TIMER": TimerIO.send_to_watch,
        "SET_TIMER": TimerIO.send_to_watch_set,
        "SET_TIME": TimeIO.send_to_watch_set,
    }

    data_received_messages = {
        CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]: AlarmsIO.on_received,
        CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]: AlarmsIO.on_received,
        CHARACTERISTICS["CASIO_DST_SETTING"]: DstForWorldCitiesIO.on_received,
        CHARACTERISTICS["CASIO_REMINDER_TIME"]: EventsIO.on_received,
        CHARACTERISTICS["CASIO_REMINDER_TITLE"]: EventsIO.on_received_title,
        CHARACTERISTICS["CASIO_TIMER"]: TimerIO.on_received,
        CHARACTERISTICS["CASIO_WORLD_CITIES"]: WorldCitiesIO.on_received,
        CHARACTERISTICS["CASIO_DST_WATCH_STATE"]: DstWatchStateIO.on_received,
        CHARACTERISTICS["CASIO_WATCH_NAME"]: WatchNameIO.on_received,
        CHARACTERISTICS["CASIO_WATCH_CONDITION"]: WatchConditionIO.on_received,
        CHARACTERISTICS["CASIO_APP_INFORMATION"]: AppInfoIO.on_received,
        CHARACTERISTICS["CASIO_BLE_FEATURES"]: ButtonPressedIO.on_received,
        CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]: SettingsIO.on_received,
        CHARACTERISTICS["CASIO_SETTING_FOR_BLE"]: TimeAdjustmentIO.on_received,
        CHARACTERISTICS["ERROR"]: ErrorIO.on_received,
        CHARACTERISTICS["UNKNOWN"]: UnknownIO.on_received,
    }

    @staticmethod
    def send_to_watch(self, connection, message):
        action = message.get("action")
        MessageDispatcher.watch_senders[action](connection, message)

    @staticmethod
    def on_received(data):
        key = data[0]
        if key not in MessageDispatcher.data_received_messages:
            print(f"Unknown key: {key}")
        else:
            print(f"Found key: {MessageDispatcher.data_received_messages[key]}")
            MessageDispatcher.data_received_messages[key](data)


# Usage example
if __name__ == "__main__":
    # Simulated messages
    sample_message = {"action": "GET_SETTINGS"}
    sample_data = "1,2,3,4,5"

    # Simulated message dispatching
    MessageDispatcher.send_to_watch(sample_message)
    MessageDispatcher.on_received(sample_data)