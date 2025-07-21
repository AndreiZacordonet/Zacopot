import socket
import threading
import time

import paramiko

from core.command_parser import command_parser
from core.filesystem import FileSystem
from models.models import CommandTypes
from utils.constants import BANNER, KEY_PATH, FS_SOURCE_PATH, DISTRO, MAX_CONNECTIONS, \
    MAX_BUFFER_SIZE, LOG_DIR
from utils.loader import fs_loader
import logging
from copy import deepcopy


# key = paramiko.RSAKey.generate(bits=2048)
# key.write_private_key_file(key_path)

class SSHServer(paramiko.ServerInterface):

    def __init__(self, addr, command_logger, username: str = 'admin', password: str = 'admin'):
        self.event = threading.Event()
        self.client_ip, self.client_port = addr
        self.command_logger = command_logger
        self.username = username
        self.password = password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.common.OPEN_SUCCEEDED
        return paramiko.common.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):      # allow only user-pass auth
        return 'password'

    def check_auth_password(self, username, password):
        self.command_logger.info(f'Client: {self.client_ip}:{self.client_port} | Type: {CommandTypes.CREDENTIALS} | Username: {repr(username)} | Password: {repr(password)}')

        if self.username == username and self.password == password:
            return paramiko.common.AUTH_SUCCESSFUL
        return paramiko.common.AUTH_SUCCESSFUL

    def check_channel_shell_request(self, channel):     # allows shell
        self.event.set()
        return True

    def check_channel_pty_request(              # allow pseudo-terminal
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        return True

    def check_channel_exec_request(self, channel, command):
        # log exec commands even if not allowed
        self.command_logger.info(
            f'Client: {self.client_ip}:{self.client_port} | Type: {CommandTypes.EXEC} | Command: {repr(command)}')

        return False


def client_handler(file_system, sock, client, addr, host_key, command_logger, error_logger, active_connections: set, active_connections_lock, fatal_event, username: str, password: str):
    client_ip, port = addr

    with active_connections_lock:       # add new connection to active connections
        active_connections.add(addr)

    # log new connection
    command_logger.info(f'Client: {client_ip}:{port} connected')

    transport = paramiko.Transport(client)
    transport.server_version = "SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7"
    transport.add_server_key(host_key)
    server = SSHServer(addr, command_logger, username, password)

    channel = None

    try:
        try:
            # set up connection
            transport.start_server(server=server)
        except paramiko.SSHException as e:
            error_logger.exception(f"Client: {client_ip}:{port} | SSHException: {e}")
            transport.close()
            client.close()
            command_logger.info(f'Client: {client_ip}:{port} disconnected')
            return
        # set up connection
        # transport.server_version = "SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7"
        # transport.start_server(server=server)

        channel = transport.accept(20)      # wait 20 sec for channel
        if channel is None:     # no channel
            return
        server.event.wait(10)               # wait 10 sec for shell request
        if not server.event.is_set():       # no shell request
            return

        # start fake shell communication
        path = file_system.PWD[1]
        prompt = f'{username}@{DISTRO}:{path}$ '
        channel.send(BANNER + prompt.encode())

        buff = b''
        command = ''

        while True:
            try:
                data = channel.recv(1024)
                if not data:
                    return

                channel.send(data)

                buff += data

                if len(buff) > MAX_BUFFER_SIZE:
                    channel.send(b'Input too long. Connection closed.\n')
                    break

                # implement backspace
                if buff and buff[-1] in (8, 127):
                    buff = buff.rstrip(b'\x7f')
                    if len(buff) > 0:
                        buff = buff[:-1]
                        channel.send(b'\b \b')
                    continue

                # if buff and buff.endswith((b'\x1b[A', b'\x1b[B', b'\x1b[C', b'\x1b[D', b'\x1b[3~')):
                #     buff = buff[:-3]
                #     channel.send(b'\b \b' * 3)
                #     continue

                if buff.endswith(b'\r') or buff.endswith(b'\n'):    # check for message ending
                    command = buff.decode().strip()

                    output = command_parser(file_system, command)

                    if output == 'exit':
                        break

                    path = file_system.PWD[1]

                    if len(output) != 0:
                        output = '\r\n' + output
                    prompt = f'{username}@{DISTRO}:{path}$ '
                    channel.send((output + '\r\n' + prompt).encode())      # send back output
                    buff = b''

                    command_logger.info(f'Client: {client_ip}:{port} | Type: {CommandTypes.SHELL} | Command: {repr(command)} | Output: {output}')

            except Exception:
                command_logger.info(f'Client: {client_ip}:{port} | Type: {CommandTypes.SHELL} | Last Command: {repr(command)}')
                error_logger.exception(f"Client: {client_ip}:{port} | Unexpected error")
                channel.close()
                fatal_event.set()  # set fatal event to propagate error
                sock.close()       # close socket so the fatal event is seen in main thread
                break

    except Exception:
        error_logger.exception(f"Client: {client_ip}:{port} | Unexpected error")
        fatal_event.set()       # set fatal event to propagate error
        if sock:
            sock.close()  # close socket so the fatal event is seen in main thread

    finally:
        if channel:
            channel.close()     # close channel if is open
        transport.close()
        client.close()

        with active_connections_lock:       # remove client from active client connections
            active_connections.remove(addr)

        command_logger.info(f'Client: {client_ip}:{port} disconnected')

        # set reference count to 0 asap
        file_system = None


def honeypot(host='0.0.0.0', port=2222, username: str = 'admin', password: str = 'admin'):
    host_key = paramiko.RSAKey(filename=KEY_PATH)

    # Command logger
    command_logger = logging.getLogger('command_logger')
    command_handler = logging.FileHandler(LOG_DIR + '/commands.log', encoding='utf-8')
    command_handler.setLevel(logging.INFO)
    command_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
    command_logger.addHandler(command_handler)
    command_logger.setLevel(logging.INFO)

    # Error logger
    error_logger = logging.getLogger('error_logger')
    error_handler = logging.FileHandler(LOG_DIR + '/errors.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s - %(message)s'))
    error_logger.addHandler(error_handler)
    error_logger.setLevel(logging.ERROR)

    # network set up
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)
    sock.settimeout(1.0)  # 1 second timeout

    active_connections = set()      # cap active connections
    active_connections_lock = threading.Lock()
    fatal_event = threading.Event()     # for error propagation

    print('Initializing filesystem...')
    file_system = FileSystem()
    fs_loader(file_system, FS_SOURCE_PATH)

    print(f'SSH server is listening on port {port}.')

    while True:
        try:
            client, addr = sock.accept()

            with active_connections_lock:       # prevent more connections if max capacity is reached
                if len(active_connections) >= MAX_CONNECTIONS:
                    client.close()
                    continue

            # create fs deep copy for each client
            fs_copy = deepcopy(file_system)

            # create daemon threads to easily stop the main process
            threading.Thread(target=client_handler, args=(fs_copy, sock, client, addr, host_key, command_logger, error_logger, active_connections, active_connections_lock, fatal_event, username, password), daemon=True).start()

        except socket.timeout:
            # check for internal exceptions
            if fatal_event.is_set():
                break
        except Exception:
            error_logger.exception(f"Unexpected error")
            break


if __name__ == '__main__':
    honeypot()
