import subprocess
import logging

logger = logging.getLogger(__name__)


class IptablesV4CMD:
    def __init__(self, binary, save_binary, restore_binary, protocol):
        self.binary = binary
        self.save_binary = save_binary
        self.restore_binary = restore_binary
        self.protocol = protocol
        self.exec_cmd = None

    def exec(self, *args):
        return None

    def save(self, *args):
        cmd = ["sh", "-c", f"{self.save_binary} {' '.join(args)}"]
        # 通过 capture_output=True 参数捕获命令的标准输出和标准错误
        process = subprocess.run(cmd, capture_output=True, text=True)
        # 返回不为 0，则表示执行出错
        if process.returncode != 0:
            err_msg = f"exec: [sh -c {' '.join(cmd)}] err: {process.stderr}"
            logger.error(err_msg)
            return "", ValueError(err_msg)
        return process.stdout.strip(), None

    def restore(self, fileName):
        cmd = ["sh", "-c", f"{self.restore_binary} < {fileName}"]
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode != 0:
            err_msg = f"exec: [sh -c {' '.join(cmd)}] err: {process.stderr}"
            logger.error(err_msg)
            return "", ValueError(err_msg)
        return process.stdout.strip(), None