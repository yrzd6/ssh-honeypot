from utils import dispose_string
from output import Output
import paramiko

CMDS = [
    "ls", "cd", "pwd", "mkdir", "rm", "cp", "mv", "touch",
    "cat", "less", "more", "head", "tail", "find", "grep", "ssh",
    "ifconfig", "netstat", "whoami", "hostname", "uname", "df",
    "free", "ps", "kill", "killall", "shutdown", "reboot", "date",
    "history", "alias", "unalias", "echo", "printf", "env", "set",
    "help", "rsync", "ping", "curl", "wget"
]

class HoneypotShell:
    def __init__(self, channel, output: Output, client_ip: str):
        self.channel = channel
        self.output = output
        self.client_ip = client_ip
        self.buffer = ""
        self.history = []
        self.history_pos = -1
        self._should_exit = False

        self.SUPPORTED_COMMANDS = {
            'logout': lambda args=None: self._logout(args),
            'su': lambda args=None: self._su(args),
            'sudo': lambda args=None: self._sudo(args),
            'passwd': lambda args=None: self._fake_command(args),
            **{cmd: lambda args=None: self._fake_command(cmd) for cmd in CMDS}
        }

    def run(self):
        self.channel.send(dispose_string("\x1b[2J\x1b[H"))  # 清屏
        self.channel.send(dispose_string(self.output.motd()))
        self.channel.send(dispose_string(self.output.prompt()))

        while not self._should_exit:
            try:
                data = self.channel.recv(1)
                if not data:
                    break

                char = data.decode("utf-8")

                if char == '\x1b':  # 处理方向键
                    seq = self.channel.recv(2)
                    if seq == b'[A':  # 上箭头
                        if self.history:
                            if self.history_pos == -1:
                                self.history_pos = len(self.history) - 1
                            elif self.history_pos > 0:
                                self.history_pos -= 1
                            self._update_line(self.history[self.history_pos])
                    elif seq == b'[B':  # 下箭头
                        if self.history and self.history_pos < len(self.history) - 1:
                            self.history_pos += 1
                            self._update_line(self.history[self.history_pos])
                        elif self.history_pos == len(self.history) - 1:
                            self.history_pos = -1
                            self._update_line("")
                    continue

                if char in ('\x7f', '\x08'):  # 退格
                    if len(self.buffer) > 0:
                        self.buffer = self.buffer[:-1]
                        self.channel.send(b'\x08 \x08')
                    continue

                if char in ("\r", "\n"):  # 回车
                    command = self.buffer.strip()
                    if command:
                        self.history.append(command)
                        self.history_pos = -1
                        self.output.run_command(self.client_ip, command)

                        if command.lower().split()[0] in self.SUPPORTED_COMMANDS:
                            parts = list(filter(None, command.split()))
                            cmd_name = parts[0].lower()
                            self.SUPPORTED_COMMANDS[cmd_name](parts)
                        else:
                            self.channel.send(dispose_string(self.output.error_msg(command=command)))

                    if not self._should_exit:
                        self.buffer = ""
                        self.channel.send(dispose_string("\n" + self.output.prompt()))
                else:
                    self.channel.send(data)
                    self.buffer += char

            except (paramiko.SSHException, EOFError, UnicodeDecodeError) as e:
                break

    def _update_line(self, new_line):
        self.channel.send(b'\r\x1b[K')
        self.channel.send(dispose_string(self.output.prompt()))
        self.buffer = new_line
        self.channel.send(new_line.encode('utf-8'))

    def _logout(self, arg):
        self.channel.send(dispose_string("\n"))
        self._should_exit = True
        self.output.connection_closed(self.client_ip, "User logged out")  # 新增退出日志
        self.channel.close()

    def _su(self, arg):
        self.channel.send(dispose_string(self.output.su_msg()))

    def _sudo(self, arg):
        self.channel.send(dispose_string(self.output.sudo_msg()))

    def _passwd(self, arg):
        self.channel.send(dispose_string(self.output.passwd_msg()))

    def _fake_command(self, arg):
        self.channel.send(dispose_string(self.output.fake_msg()))