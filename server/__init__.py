import socketserver
import parser

nameIpMap = {}


class ClientHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print("Handling message from ", self.client_address)
        data = self.rfile.readline().decode("utf-8")

        print("Received data:", data)
        if data.startswith("HELLO-FROM"):
            name = data[len("HELLO-FROM"):].strip()
            nameIpMap[name] = self.client_address
            print("name:", name, "ip:", nameIpMap[name])


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), ClientHandler)
    print("Started server")
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
