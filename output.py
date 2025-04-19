from getpass import getuser
from utils import send_log

class Output:
    def __init__(self, config):
        self.config = config

    def motd(self):
        return self.config['messages']['motd'].format(endl='\r\n')

    def error_msg(self, command):
        return self.config['messages']['error_msg'].format(command=command, endl='\r\n')

    def prompt(self, username=None):
        if username is None:
            username = getuser().lower()
        return self.config['messages']['prompt'].format(username=username, endl='\r\n', space=' ')

    def su_msg(self):
        return self.config['messages']['su_error'].format(endl='\r\n')

    def sudo_msg(self, username=None):
        if username is None:
            username = getuser().lower()
        return self.config['messages']['sudo_error'].format(endl='\r\n', user=username)

    def passwd_msg(self):
        return self.config['messages']['passwd_error'].format(endl='\r\n')

    def fake_msg(self):
        return self.config['messages']['fake_cmd_error'].format(endl='\r\n')

    def login_success(self, ip, username, password):
        msg = self.config['output']['login_success'].format(ip=ip, username=username, password=password)
        send_log("+", msg)

    def login_failed(self, ip, username, password):
        msg = self.config['output']['login_failed'].format(ip=ip, username=username, password=password)
        send_log("-", msg)

    def new_connection(self, ip):
        msg = self.config['output']['new_connection'].format(ip=ip)
        send_log("+", msg)

    def shutdown_server(self):
        msg = self.config['output']['shutdown_msg']
        send_log("!", msg)

    def startup(self, host, port):
        msg = self.config['output']['startup_msg'].format(host=host, port=port)
        send_log("*", msg)

    def no_channel(self, ip):
        msg = self.config['output']['no_channel_msg'].format(ip=ip)
        send_log("-", msg)

    def connection_error(self, ip, error):
        msg = self.config['output']['connection_error_msg'].format(ip=ip, error=error)
        send_log("-", msg)

    def rsa_key_error(self):
        msg = self.config['output']['rsa_key_error']
        send_log("-", msg)

    def run_command(self, ip, command):
        msg = self.config['output']['run_command'].format(ip=ip, command=command)
        send_log("!", msg)
        return msg

    def connection_closed(self, ip, reason=""):
        msg = self.config['output']['connection_closed_msg'].format(
ip=ip,
            reason=f": {reason}" if reason else ""
        )
        send_log("-", msg)