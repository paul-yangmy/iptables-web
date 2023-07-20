import random
import time
import json
import http.server
import json
import hashlib


def init():
    random.seed(time.time())


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
