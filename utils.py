from time import strftime, localtime
import os

LOG_NAME = f'./logs/ssh-honeypot-{strftime("%Y%m%d%H%M%S", localtime())}.log'

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def dispose_string(string):
    """处理字符串格式，替换换行符并编码"""
    return string.replace('\n', '\r\n').encode('utf-8')

def send_log(log_type, log_message):
    log = f"[{strftime('%Y-%m-%d %H:%M:%S', localtime())}] [{log_type}] {log_message}"
    with open(LOG_NAME, 'a') as f:
        f.write(log + '\n')
    print(log)


if __name__ == '__main__':
    send_log('test', 'Running successfully!')

# [!] 重要，提示
# [*] 普通信息
# [+] 成功信息，加入
# [-] 错误信息，退出
# [@] 作者相关信息
# [#] 代码相关信息
