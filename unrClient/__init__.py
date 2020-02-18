import socket
from sys import stdin
from threading import Thread


class UdpConnection:
    def __init__(self, sock, hostname, port, timeout):
        self.socket = sock
        self.hostname = hostname
        self.port = port
        self.socket.settimeout(timeout)
        self.socket.connect()

    def send(self, message):
        self.socket.sendTo("{}\n".format(message).encode("UTF-8"), (self.hostname, self.port))

    def receive(self, buffer):
        try:
            data = self.socket.recv(buffer)
            return data.decode("UTF-8")
        except socket.timeout:
            print("Socket timeout!")


class User:
    def __init__(self, name, udpConn):
        self.name = name
        self.udpConn = udpConn
        self.connected = True


def represents_positive_int(s):
    try:
        return int(s)
    except ValueError:
        return -1


def create_udp_socket(timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = input("Specify the hostname (IP address): ")
    port = input("Specify the port number: ")
    while represents_positive_int(port) < 0:
        port = input("Port number should be a positive integer. Try again: ")
    return UdpConnection(sock, hostname, port, timeout)


def try_create_new_user(udpConn: UdpConnection):
    name = input("Specify a username: ")
    udpConn.send("HELLO-FROM {}".format(name))
    data = udpConn.receive(2048)
    while True:
        if data is None:
            print("Something is wrong with the connection")
        elif data.startswith("HELLO {}".format(name)):
            return User(name, udpConn)
        elif data.startswith("IN-USE"):
            print("This username is already in use\n")
        elif data.startswith("BUSY"):
            print("Server is to busy, try again later\n")
        retry = input("Try again? (Y/N)")
        if retry.lower() == "y":
            return


def handle_user_input(user: User):
    while user.connected:
        line = stdin.readline().split()
        if len(line) == 0:
            continue
        elif line[0] == "!quit":
            user.connected = False
            break
        elif line[0] == "!who":
            user.udpConn.send("WHO")
        elif line[0].startswith('@'):
            target = line[0][1:]
            message = ' '.join(line[1:])
            user.udpConn.send("SEND {} {}".format(target, message))


def handle_server_input(user):
    while user.connected:
        line = user.udpConn.receive(2048).split()
        if len(line) == 0:
            user.connected = False
            break
        elif line[0] == "DELIVERY":
            if len(line) == 1:
                continue
            name = line[1]
            message = ' '.join(line[2:])
            print(name, "says:", message)
        elif line[0] == "WHO-OK":
            users = ", ".join(line[1:])
            print("Online users:", users)


def handle_new_user(user):
    user_t = Thread(target=handle_user_input, args=(user,))
    server_t = Thread(target=handle_server_input, args=(user,))
    user_t.start()
    server_t.start()
    user_t.join()
    server_t.join()


if __name__ == "__main__":
    udpConn = create_udp_socket(1)
    user = try_create_new_user(udpConn)
    if user is not None:
        handle_new_user(user)
    print("Exiting...")
    udpConn.socket.close()
