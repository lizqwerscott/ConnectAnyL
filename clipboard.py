import base64
import subprocess

# use xclip only support linux, need other systemc support


class ClipboardData:
    type: str
    data: str

    def __init__(self, type: str, data: str) -> None:
        self.type = type
        self.data = data

    def empty(self):
        return self.data == ""


def get_clipboard_data() -> ClipboardData | None:
    """
    获取剪贴板中的数据。

    Returns:
        dict: 剪贴板中的数据和类型，格式为 {'type': 'text'/'image', 'data': 数据内容或文件路径}
    """

    # 尝试获取文本数据
    try:
        text_data = subprocess.check_output(
            ["xclip", "-selection", "clipboard", "-o"], stderr=subprocess.STDOUT
        )
        return ClipboardData("Text", text_data.decode("utf-8"))
    except Exception as e:
        pass

    # 尝试获取图像数据
    try:
        image_data = subprocess.check_output(
            ["xclip", "-selection", "clipboard", "-t", "image/png", "-o"]
        )
        print("get image")
        image_path = "/tmp/clipboard_image.png"
        with open(image_path, "wb") as f:
            f.write(image_data)
        base64_bytes = base64.b64encode(image_data)
        base64_string = base64_bytes.decode()
        return ClipboardData("Image", base64_string)
    except Exception as e:
        pass

    # 尝试获取图像数据
    try:
        image_data = subprocess.check_output(
            ["xclip", "-selection", "clipboard", "-t", "image/jpeg", "-o"]
        )
        print("get image")
        image_path = "/tmp/clipboard_image.png"
        with open(image_path, "wb") as f:
            f.write(image_data)
        base64_bytes = base64.b64encode(image_data)
        base64_string = base64_bytes.decode()
        return ClipboardData("Image", base64_string)
    except Exception as e:
        pass

    return None


def set_clipboard_data(data: ClipboardData):
    """
    将数据写入剪贴板。

    Args:
        data (str): 要写入剪贴板的数据。
    """
    if data.type == "Text":
        process = subprocess.Popen(
            ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE
        )
        process.communicate(input=data.data.encode("utf-8"))
    elif data.type == "Image":
        # with open(data, "rb") as f:
        #     image_data = f.read()
        image_data = base64.b64decode(data.data)
        process = subprocess.Popen(
            ["xclip", "-selection", "clipboard", "-t", "image/png"],
            stdin=subprocess.PIPE,
        )
        process.communicate(input=image_data)


if __name__ == "__main__":
    pass
