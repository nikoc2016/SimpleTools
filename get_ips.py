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
    return [line.strip() for line in ip_str.splitlines() if line.strip() and line.strip()[0].isdigit()]

def extract_filtered_ipv4s(text):
    """匹配 eth 接口后的几行中 inet 开头的 IP（去除 10.x），最终排序返回"""
    results = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.search(r'^\d+:\s+eth\d+', line.strip()):
            # 检查接下来最多 5 行，寻找 inet 开头的 IPv4 地址
            for j in range(1, 6):
                if i + j >= len(lines):
                    break
                next_line = lines[i + j].strip()
                if next_line.startswith("inet "):
                    ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', next_line)
                    if ip_match:
                        ip = ip_match.group(1)
                        if not ip.startswith("10."):
                            results.append(ip)
    return sorted(results)

def ssh_and_get_ip_addrs(ip):
    try:
        # 获取 ip addr
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", ip, "ip addr"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            text=True
        )
        if result.returncode != 0:
            return f"{ip} ERROR: {result.stderr.strip()}"

        ipv4s = extract_filtered_ipv4s(result.stdout)

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
        if "timed out" in str(e):
            return f"{ip}"
        else:
            return f"{ip} ERROR: {str(e)}"

if __name__ == "__main__":
    for ip in ip_to_list(ip_str):
        print(ssh_and_get_ip_addrs(ip))