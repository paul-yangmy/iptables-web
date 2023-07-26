import os
import logging
import tempfile

from utils.func import shell_exec, split_and_trim_space

logger = logging.getLogger(__name__)


def new_iptables():
    return IptablesV4CMD()


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
                err_msg = f"Import rule error. err: {error}"
                logger.error(err_msg)
                raise ValueError(err_msg)
        finally:
            os.remove(temp_file_path)

    # 删除 iptables -D INPUT ${行数}
    def delete_rule(self, chain, rule_id):
        if not chain or not rule_id:
            err_msg = f"DeleteRule args error. chain:{chain} table_id:{rule_id}"
            logger.error(err_msg)
            return ValueError(err_msg)
        cmd = [self.binary, "-D", chain, rule_id]
        _, error = shell_exec(cmd)
        return error

    # sudo sh -c "iptables-save > iptables-rules.txt"
    def get_rule_info(self, chain, rule_id):
        if not chain or not rule_id:
            err_msg = "GetRuleInfo args error. chain:{}, id:{}".format(chain, rule_id)
            logger.error(err_msg)
            return "", ValueError(err_msg)
        try:
            output = self.save(chain, rule_id)
            rule_list = split_and_trim_space(output, "\n")
            rule_id_int = int(rule_id)
            if len(rule_list) < rule_id_int:
                err_msg = "GetRuleInfo rule not found"
                logger.error(err_msg)
                return "", ValueError(err_msg)
            return rule_list[rule_id_int - 1], None
        except Exception as e:
            logger.error(e)
            return "", e
