import requests
import socket
import logging

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s]: %(message)s", level=logging.INFO
)


def web_post(default_host: str, command: str, data) -> dict | None:
    url = "http://{}:8686{}".format(default_host, command)
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


def generate_device(device_id: str) -> dict:
    return {"id": device_id, "type": "Linux", "name": socket.gethostname()}


def generate_clipboard_data(data: str) -> dict:
    return {"type": "text", "data": data, "date": "114514"}


def login(default_host: str, user_name: str, device_id: str) -> bool:
    body = {}
    body["device"] = generate_device(device_id)
    body["name"] = user_name
    res = handle_res(web_post(default_host, "/user/adduser", body))
    if res != None:
        return res
    else:
        return False


def add_clipboard_message(default_host: str, device_id: str, clipboard: str) -> bool:
    body = {}
    body["device"] = generate_device(device_id)
    body["message"] = generate_clipboard_data(clipboard)
    res = handle_res(web_post(default_host, "/message/addmessage", body))
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
