import requests
import socket
import logging
import time

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s]: %(message)s", level=logging.INFO
)


def web_post(default_host: str, command: str, data):
    url = "http://{}{}".format(default_host, command)
    # url = "{}{}".format(default_host, command)
    res = None
    try:
        res = requests.post(url, json=data).json()
    except:
        logging.error("http post in {}".format(url))
    return res


def handle_res(res):
    if res != None:
        if res["code"] == 200:
            logging.info("res: {}".format(res["msg"]))
            return res["data"]
        else:
            logging.error(
                "server error msg: {}, code: {}".format(res["msg"], res["code"])
            )
    return None

def generate_input_device() -> dict:
    return {"type": "Linux", "name": socket.gethostname()}

def generate_device() -> dict:
    return {"type": "Linux", "name": socket.gethostname(), "notification": ""}


def generate_clipboard_data(data: str) -> dict:
    return {"type": "text", "data": data, "date": int(round(time.time() * 1000))}


def login(default_host: str, server_port: int, user_name: str) -> bool:
    body = {}
    body["device"] = generate_device()
    body["name"] = user_name
    res = handle_res(web_post("{}:{}".format(default_host, server_port), "/user/adduser", body))
    if res != None:
        return res
    else:
        return False


def add_clipboard_message(default_host: str, server_port: int, clipboard: str) -> bool:
    body = {}
    body["device"] = generate_device()
    body["message"] = generate_clipboard_data(clipboard)
    res = handle_res(web_post("{}:{}".format(default_host, server_port), "/message/addmessage", body))
    if res != None:
        return res
    else:
        return False


def update_base_message(defualt_host: str, device_id: str):
    pass


if __name__ == "__main__":
    dev_host = "http://127.0.0.1:4523/m1/2074769-0-default"
    # login(dev_host, "lizqwer", "111")
    # add_clipboard_message(dev_host, "111", "hahaha")
