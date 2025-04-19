import paramiko
import socket
import threading
from paramiko import ServerInterface
from paramiko.common import AUTH_SUCCESSFUL, AUTH_FAILED, OPEN_SUCCEEDED, OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
from shell import HoneypotShell

class FakeSSHServer(ServerInterface):
    def __init__(self, output, client_ip):
        self.username = None
        self.password = None
        self.output = output
        self.client_ip = client_ip

    def check_auth_password(self, username, password):
        self.username = username
        self.password = password
        if password == self.output.config['settings']['password']:
            self.output.login_success(self.client_ip, username, password)
            return AUTH_SUCCESSFUL
        else:
            self.output.login_failed(self.client_ip, username, password)
            return AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return OPEN_SUCCEEDED
        return OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        return False

    def get_allowed_auths(self, username):
        return "password"

def handle_connection(client_sock, client_addr, config, rsa_key, output):
    client_ip = client_addr[0]
    output.new_connection(client_ip)

    transport = None
    try:
        transport = paramiko.Transport(client_sock)
        transport.add_server_key(rsa_key)
        transport.start_server(server=FakeSSHServer(output, client_ip))

        channel = transport.accept(20)
        if channel is None:
            output.no_channel(client_ip)
            return

        shell = HoneypotShell(channel, output, client_ip)
        shell.run()

    except Exception as e:
        output.connection_error(client_ip, str(e))
        output.connection_closed(client_ip, f"Error: {str(e)}")  # 新增错误关闭记录
    else:
        output.connection_closed(client_ip, "Client disconnected")  # 新增正常关闭记录
    finally:
        if transport:
            transport.close()