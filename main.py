import json
import logging
import threading
from pathlib import Path
from time import sleep
from typing import TypedDict

import websocket

import web
from clipboard import ClipboardData, get_clipboard_data, set_clipboard_data


class Config(TypedDict):
    name: str
    host: str
    server_port: int


DEFAULT_CONFIG: Config = {
    "name": "",
    "host": "127.0.0.1",
    "server_port": 22010,
}


class ClipboardManager(threading.Thread):
    def __init__(self, name: str, default_host: str, server_port: int) -> None:
        threading.Thread.__init__(self)
        self.threadId = "1"
        self.name = "1"
        self.delay = 1
        self.clipboard_data = get_clipboard_data()

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
            self.clipboard_data = ClipboardData("Text", clipboard["data"])
            print(message)
        elif clipboard["type"] == "Image":
            self.clipboard_data = ClipboardData("Image", clipboard["data"])
            print("image")
        if self.clipboard_data is not None:
            set_clipboard_data(self.clipboard_data)

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
            clipboard_data = get_clipboard_data()
            if clipboard_data is not None and not clipboard_data.empty():
                if self.clipboard_data is not None:
                    if (
                        clipboard_data.type != self.clipboard_data.type
                        or clipboard_data.data != self.clipboard_data.data
                    ):
                        # 添加新剪切板
                        self.clipboard_data = clipboard_data
                        web.add_clipboard_message(
                            self.default_host, self.server_port, self.clipboard_data
                        )
                else:
                    # 添加新剪切板
                    self.clipboard_data = clipboard_data
                    web.add_clipboard_message(
                        self.default_host, self.server_port, self.clipboard_data
                    )

            sleep(1)


def load_config() -> Config:
    config_dir = Path("./config/")
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "config.json"

    config = DEFAULT_CONFIG.copy()
    if not config_path.exists():
        name = input("Please input name: ")
        config = DEFAULT_CONFIG.copy()
        config["name"] = name
        _ = config_path.write_text(json.dumps(config, indent=2))
    else:
        with config_path.open("r", encoding="utf-8") as f:
            loaded: dict[str, object] = json.load(f)

        config["name"] = str(loaded.get("name", DEFAULT_CONFIG["name"]))
        config["host"] = str(loaded.get("host", DEFAULT_CONFIG["host"]))

        server_port = loaded.get("server_port", DEFAULT_CONFIG["server_port"])
        try:
            config["server_port"] = int(str(server_port))
        except (TypeError, ValueError):
            # 如果无法转为 int，使用默认值
            config["server_port"] = DEFAULT_CONFIG["server_port"]

    return config


def main():
    configs = load_config()

    res = web.login(configs["host"], configs["server_port"], configs["name"])
    if res:
        manager = ClipboardManager(
            configs["name"], configs["host"], configs["server_port"]
        )
        manager.start()
        manager.run_ws()
    else:
        logging.error("login failed")
        exit(1)


if __name__ == "__main__":
    main()
