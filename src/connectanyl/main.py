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
    def __init__(self, name: str, default_host: str, server_port: int) -> None:
        threading.Thread.__init__(self)
        self.threadId = "1"
        self.name = "1"
        self.delay = 1
        self.clipboard_data = pyperclip.paste()

        self.user_name = name
        self.default_host = default_host
        self.server_port = server_port

        self.ws = websocket.WebSocketApp(
            "ws://{}:{}/ws".format(default_host, server_port),
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
            on_message=self.on_message,
        )

    def on_message(self, ws, message):
        clipboard = json.loads(message)
        if clipboard["type"] == "Text":
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
        body["device"] = web.generate_input_device()
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
                    self.default_host, self.server_port, self.clipboard_data
                )
            sleep(1)
        print("结束")

def load_config() -> dict:
    default_path = Path("./config/")
    if not os.path.exists(default_path):
        os.makedirs(default_path)

    config_path = os.path.join(default_path, "config.json")

    configs = { "name": "", "host": "127.0.0.1", "server_port": 22010 }

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
    print(configs)
    res = web.login(configs["host"], configs["server_port"], configs["name"])
    if res:
        manager = ClipboardManager(configs["name"], configs["host"], configs["server_port"])
        manager.start()
        manager.run_ws()
    else:
        logging.error("login failed")
        exit(1)
