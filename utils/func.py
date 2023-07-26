import random
import subprocess
import time
import json
import http.server
import json
import hashlib

from utils.iptables import logger


def init():
    random.seed(time.time())


def shell_exec(cmd):
    # 通过 capture_output=True 参数捕获命令的标准输出和标准错误
    # run函数第一个参数为要执行的命令和命令参数字符串列表（args），如果使用字符串需要使用shell=True参数
    process = subprocess.run(cmd, capture_output=True, text=True)
    # 返回不为 0，则表示执行出错
    if process.returncode != 0:
        err_msg = f"exec: [{' '.join(cmd)}] err: {process.stderr}"
        logger.error(err_msg)
        return "", ValueError(err_msg)
    return process.stdout.strip(), None


def split_and_trim_space(s, sep):
    res = s.split(sep)
    res = [item.strip() for item in res]
    return res


def json_encoding(data):
    return json.dumps(data).encode('utf-8')


def output(w, err, data):
    code = 0
    msg = "OK"
    if err is not None:
        code = 1
        msg = str(err)

    w.setHeader("Content-Type", "application/json")
    w.setHeader("Access-Control-Allow-Origin", "*")
    w.setHeader("Access-Control-Allow-Headers", "Content-Type")
    w.send_response(http.server.HTTPStatus.OK)

    out = {
        "code": code,
        "msg": msg,
        "data": data
    }
    w.write(json_encoding(out))


def float_to_string(num):
    # to convert a float number to a string
    return "{:.2f}".format(num)


def md5_bytes(s):
    ret = hashlib.md5(s).digest()
    return ret.hex()
