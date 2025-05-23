import subprocess
import re

# 示例 IP 列表，替换为你自己的列表
ip_str = """
kpy
183.240.210.68
183.240.210.71
183.240.210.72
183.240.210.73
183.240.210.91
183.240.210.94
183.240.210.98
183.240.210.105
183.240.210.107
183.240.210.121

zenlayer
183.36.41.192
120.241.158.59
61.241.62.171
183.36.41.75
183.36.41.86
120.240.171.224
61.241.63.240
61.241.62.175
"""

def ip_to_list(ip_str):
    return [line.strip() for line in ip_str.splitlines() if line.strip() and line.strip()[0].isnumeric()]

def extract_ipv4s(text):
    """从文本中提取所有 IPv4 地址"""
    return re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)


def ssh_and_get_ip_addrs(ip):
    """通过 ssh 执行 `ip addr` 并提取所有 IPv4 地址"""
    try:
        # 执行 SSH 命令，跳过 host key 检查
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", ip, "ip addr"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            text=True
        )
        if result.returncode != 0:
            return f"{ip} ERROR: {result.stderr.strip()}"

        ipv4s = extract_ipv4s(result.stdout)

        # 获取主机名
        hostname_result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", ip, "hostname"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            text=True
        )
        hostname = hostname_result.stdout.strip() if hostname_result.returncode == 0 else "unknown"

        return f"{ip} {hostname} {' '.join(ipv4s)}"

    except Exception as e:
        return f"{ip} ERROR: {str(e)}"


if __name__ == "__main__":
    for ip in ip_to_list(ip_str):
        print(ssh_and_get_ip_addrs(ip))
