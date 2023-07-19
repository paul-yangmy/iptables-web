import os
import subprocess
import logging
import tempfile

logger = logging.getLogger(__name__)


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


class IptablesV4CMD:
    def __init__(self, binary='sudo iptables',
                 save_binary='iptables-save',
                 restore_binary='iptables-restore'):
        self.binary = binary
        self.save_binary = save_binary
        self.restore_binary = restore_binary
    # iptables命令支持配置不同的表(table),每个表用于管理不同类型的规则.
    # 常见的表包括filter表（默认表，用于过滤规则）、nat表（用于网络地址转换）、mangle表（用于修改报文）、raw表（用于处理原始数据包）等。
    # 如果使用iptables命令而没有指定-t参数,iptables将默认使用filter表.

    # 获取iptables版本信息
    def version(self):
        cmd = [self.binary, "--version"]
        return shell_exec(cmd)

    # 执行iptables命令
    def exec(self, *param):
        args = [arg.strip() for arg in param if arg.strip()]
        cmd = [self.binary, *args]
        return shell_exec(cmd)

    # sudo sh -c "iptables-save > iptables-rules.txt"
    def save(self, *args):
        cmd = ["sudo", "sh", "-c", f"{self.save_binary} {' '.join(args)}"]
        return shell_exec(cmd)

    # sudo sh -c "iptables-restore < iptables-rules.txt"
    def restore(self, fileName):
        cmd = ["sudo", "sh", "-c", f"{self.restore_binary} < {fileName}"]
        return shell_exec(cmd)

    # 导出
    def export_file(self, table, chain):
        args = []
        if table:
            args.append(table)
        if chain:
            args.append(chain)
        return self.save(*args)

    # 导入
    def import_file(self, rule):
        if not rule:
            return None
        try:
            # 使用 NamedTemporaryFile 创建了一个临时文件
            # 使用dir来指定路径, 使用prefix来指定临时文件的前缀, 使用suffix来指定临时文件的后缀
            # 将规则写入临时表/tmp/iptables.rule
            with tempfile.NamedTemporaryFile(mode="w", dir='/tmp',
                                             prefix='iptables', suffix='.rule',
                                             delete=False) as temp_file:
                temp_file.write(rule)
                # temp_file.name 来获取临时文件的完整路径
                temp_file_path = temp_file.name
            # 执行规则的导入操作，并在导入完成后删除临时文件
            _, error = self.restore(temp_file_path)
            if error:
                raise ValueError(f"Import rule error. err: {error}")
        finally:
            os.remove(temp_file_path)

    # 删除 iptables -D INPUT ${行数}
    def delete_rule(self, table, chain, table_id):
        if not table or not chain or not table_id:
            return ValueError(f"DeleteRule args error. table:{table} chain:{chain} table_id:{table_id}")
        cmd = [self.binary, "-D", chain, table_id]
        _, error = self.iptables(cmd)
        return error
