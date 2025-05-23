import subprocess
import re

# 示例 IP 列表，替换为你自己的列表
with open("get_ips.txt", "r") as f:
    IP_STR = f.read()

def ip_to_list(ip_str):
    return [line.strip() for line in ip_str.splitlines() if line.strip() and line.strip()[0].isdigit()]

def extract_filtered_ipv4s(text, exclude_ip=None):
    """匹配 eth 接口后的几行中 inet 开头的 IP（去除 10.x 和 ssh 的目标 IP），最终排序返回"""
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
                        if not ip.startswith("10.") and ip != exclude_ip:
                            results.append(ip)
    return sorted(results)


def ssh_and_get_ip_addrs(ip):
    try:
        # 获取 ip addr
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", ip, "ip addr"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2,
            text=True
        )
        if result.returncode != 0:
            return f"{ip} ERROR: {result.stderr.strip()}"

        ipv4s = extract_filtered_ipv4s(result.stdout, exclude_ip=ip)

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
    for ip in ip_to_list(IP_STR):
        print(ssh_and_get_ip_addrs(ip))