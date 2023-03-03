from time import sleep
import pyperclip
import threading
import websocket
import web
import logging
import json
import os
from pathlib import Path
import uuid


class ClipboardManager(threading.Thread):
    def __init__(self, name: str, device_id: str, default_host: str) -> None:
        threading.Thread.__init__(self)
        self.threadId = "1"
        self.name = "1"
        self.delay = 1
        self.clipboard_data = pyperclip.paste()

        self.user_name = name
        self.device_id = device_id
        self.default_host = default_host

        self.ws = websocket.WebSocketApp(
            "ws://{}:8687/clipboard".format(default_host),
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
            on_message=self.on_message,
        )

    def on_message(self, ws, message):
        clipboard = json.loads(message)
        if clipboard["type"] == "text":
            self.clipboard_data = clipboard["data"]
            pyperclip.copy(self.clipboard_data)
        print(message)

    def on_error(self, ws, error):
        logging.error("ws error: {}".format(error))

    def on_close(self, ws, close_status_code, close_msg):
        logging.info("ws closed code: {}, msg: {}".format(close_status_code, close_msg))

    def on_open(self, ws):
        logging.info("ws open connection")
        body = {}
        body["device"] = web.generate_device(self.device_id)
        body["type"] = "init"
        ws.send(json.dumps(body))

    def run_ws(self):
        self.ws.run_forever(reconnect=2)

    def run(self):
        print("开始")
        while True:
            clipboard_data = pyperclip.paste()
            if clipboard_data != "" and clipboard_data != self.clipboard_data:
                # 添加新剪切板
                self.clipboard_data = clipboard_data
                web.add_clipboard_message(
                    self.default_host, self.device_id, self.clipboard_data
                )
            sleep(1)
        print("结束")

def load_config() -> dict:
    default_path = Path("~/.connect-any-l/config/").expanduser()
    if not os.path.exists(default_path):
        os.makedirs(default_path)

    config_path = os.path.join(default_path, "config.json")

    configs = { "name": "", "id": str(uuid.uuid1()), "host": "101.42.233.83" }

    if not os.path.exists(config_path):
        name = input("Please input name:")
        configs["name"] = name
        with open(config_path, "w") as f:
            json.dump(configs, f)
    else:
        with open(config_path, "r") as f:
            configs = json.load(f)

    return configs

if __name__ == "__main__":
    configs = load_config()
    manager = ClipboardManager(configs["name"], configs["id"], configs["host"])

    manager.start()
    manager.run_ws()
