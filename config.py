import configparser
import os, sys
import paramiko
from utils import send_log

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")
RSA_KEY_PATH = os.path.join(CONFIG_DIR, "rsa_key.pem")

MOTD = """\
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-76-generic x86_64)
            
* Documentation:  https://help.ubuntu.com
* Management:     https://landscape.canonical.com
* Support:        https://ubuntu.com/advantage
{endl}"""


def load_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    config = configparser.ConfigParser()

    if not os.path.exists(CONFIG_FILE):
        send_log("+", f"Creating new config file: {CONFIG_FILE}")
        config['settings'] = {
            'port': '22',
            'password': '123456'
        }
        config['messages'] = {
            'motd': MOTD,
            'prompt': '{username}@ubuntu:~${space}',
            'error_msg': '{endl}bash: {command}: command not found',
            'su_error': '{endl}su: faild to execute /bin/bash: Permission denied.',
            'sudo_error': '{endl}{user} is not in the sudoers file. This incident will be reported.',
            'passwd_error': '{endl}passwd: Authentication token manipulation error.',
            'fake_cmd_error': '{endl}This command is not available.'
        }
        config['output'] = {
            'login_success': 'Login success - IP: {ip} | Username: {username} | Password: {password}',
            'login_failed': 'Failed Login - IP: {ip} | Username: {username} | Password: {password}',
            'new_connection': 'New connection from: {ip}',
            'connection_closed_msg': 'Connection closed from {ip}{reason}',
            'shutdown_msg': 'Shutting down honeypot...',
            'startup_msg': 'SSH Honeypot by yrzd6 is running on {host}:{port}...',
            'no_channel_msg': 'No channel for {ip}',
            'connection_error_msg': 'Error handling connection from {ip}: {error}',
            'rsa_key_error': 'Invalid RSA key in config, generating new key...',
            'run_command': '{ip} - Running command: {command}'
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            config.write(f)
        send_log("*", f"Config file created: {CONFIG_FILE}")

    config.read(CONFIG_FILE, encoding='utf-8')

    rsa_key = None
    if os.path.exists(RSA_KEY_PATH):
        try:
            rsa_key = paramiko.RSAKey(filename=RSA_KEY_PATH)
            send_log("*", f"Loaded existing RSA key from {RSA_KEY_PATH}")
        except Exception as e:
            send_log("-", f"Failed to load RSA key: {str(e)}. Generating new key...")
            rsa_key = paramiko.RSAKey.generate(2048)
            rsa_key.write_private_key_file(RSA_KEY_PATH)
            send_log("+", f"Created new RSA key at {RSA_KEY_PATH}")
    else:
        rsa_key = paramiko.RSAKey.generate(2048)
        rsa_key.write_private_key_file(RSA_KEY_PATH)
        send_log("+", f"Created new RSA key at {RSA_KEY_PATH}")

    return config, rsa_key