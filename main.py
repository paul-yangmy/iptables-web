import argparse
import logging
import os
import re
import http.server
import socketserver
import sys

logging.basicConfig(
    level=logging.DEBUG,
    filename="./logger.log",
    filemode="a",
    # 日志格式
    format="%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s",
)


def init():
    # 验证表名链名，防止注入
    verify_args = re.compile(r'^[0-9A-z_-]+$')
    # 密码复杂度校验
    password_complexity_regex = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=]).*$')

    global username, password, port, verify_args
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', default="admin", help='login username')
    parser.add_argument('-p', default="gOh#XlmO8TDfv1kf", help='login password')
    parser.add_argument('-P', default="10001", help='http listen port')
    args = parser.parse_args()
    # 解析docker参数
    docker_username = os.getenv("IPTABLES_WEB_USERNAME")
    docker_password = os.getenv("IPTABLES_WEB_PASSWORD")
    docker_port = os.getenv("IPTABLES_WEB_PORT")
    # 初始化参数
    if docker_username is None and docker_password is None and docker_port is None:
        if not password_complexity_regex.match(args.p):
            logger.error("密码复杂度不符合要求")
            sys.exit(1)
        else:
            username = args.u
            password = args.p
            port = args.P
    else:  # docker执行
        if not password_complexity_regex.match(docker_password):
            logger.error("密码复杂度不符合要求")
            sys.exit(1)
        else:
            username = docker_username
            password = docker_password
            port = docker_port


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    init()
    # 这里可以继续编写你的主程序逻辑