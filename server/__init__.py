import socketserver
import parser

nameIpMap = {}


class ClientHandler(socketserver.StreamRequestHandler):
    def handle(self):
        print("Handling message from ", self.client_address)
        data = self.rfile.readline().decode("utf-8").split()
        print("Received data:", data)

        if data[0] == "HELLO-FROM":
            if(len(data) > 2):
                self.wfile.write("BAD-RQST-BODY\n")
            else:
                name = data[1]
                nameIpMap[name] = self.client_address
                print("name:", name, "ip:", nameIpMap[name])
                self.wfile.write("HELLO {}\n ".format(name).encode("utf-8"))

        elif data[0] == "WHO":
            print("WHO-OK {}\n".format(nameIpMap.keys()))
            self.wfile.write("WHO-OK {}\n".format(nameIpMap.keys()))


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), ClientHandler)
    print("Started server")
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
