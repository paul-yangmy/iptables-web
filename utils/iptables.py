import os
import subprocess
import logging
import tempfile

logger = logging.getLogger(__name__)


def shell_exec(cmd):
    # 通过 capture_output=True 参数捕获命令的标准输出和标准错误
    process = subprocess.run(cmd, capture_output=True, text=True)
    # 返回不为 0，则表示执行出错
    if process.returncode != 0:
        err_msg = f"exec: [{' '.join(cmd)}] err: {process.stderr}"
        logger.error(err_msg)
        return "", ValueError(err_msg)
    return process.stdout.strip(), None


class IptablesV4CMD:
    def __init__(self, binary, save_binary, restore_binary, protocol):
        self.binary = binary
        self.save_binary = save_binary
        self.restore_binary = restore_binary
        self.protocol = protocol
        self.exec_cmd = None

    def exec(self, *param):
        args = [arg.strip() for arg in param if arg.strip()]
        cmd = [self.binary, *args]
        return shell_exec(cmd)

    def save(self, *args):
        cmd = ["sh", "-c", f"{self.save_binary} {' '.join(args)}"]
        return shell_exec(cmd)

    def restore(self, fileName):
        cmd = ["sh", "-c", f"{self.restore_binary} < {fileName}"]
        return shell_exec(cmd)

    def export_file(self, table, chain):
        args = []
        if table:
            args.append(table)
        if chain:
            args.append(chain)
        return self.save(*args)

    def import_file(self, rule):
        if not rule:
            return None
        try:
            # 使用 NamedTemporaryFile 创建了一个临时文件, 使用prefix来指定临时文件的前缀，使用suffix来指定临时文件的后缀
            with tempfile.NamedTemporaryFile(mode="w", prefix='iptables', suffix='.rule', delete=False) as temp_file:
                temp_file.write(rule)
                # temp_file.name 来获取临时文件的完整路径
                temp_file_path = temp_file.name
            # 执行规则的导入操作，并在导入完成后删除临时文件
            _, error = self.restore(temp_file_path)
            if error:
                raise ValueError(f"Import rule error. err: {error}")
        finally:
            os.remove(temp_file_path)

    def delete_rule(self, table, chain, id):
        if not table or not chain or not id:
            return ValueError(f"DeleteRule args error. table:{table} chain:{chain} id:{id}")

        _, error = self.iptables("-t", table, "-D", chain, id)
        return error
