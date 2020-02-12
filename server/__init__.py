import socketserver


class ClientHandler(socketserver.StreamRequestHandler):
    nameSockMap = {}

    def handle(self):
        print("Handling message from ", self.client_address)
        thisname = ""
        while True:
            data = self.rfile.readline().decode("utf-8").split()
            print("Received data:", data)

            if len(data) == 0:
                if thisname in self.nameSockMap:
                    del self.nameSockMap[thisname]
                print("EOF")
                break

            if data[0] == "HELLO-FROM":
                if len(data) > 2:
                    self.wfile.write("BAD-RQST-BODY\n".encode("utf-8"))
                else:
                    thisname = data[1]
                    if thisname in self.nameSockMap:
                        print("name:", thisname, "is already in use")
                        self.wfile.write("IN-USE\n".encode("utf-8"))
                    else:
                        self.nameSockMap[thisname] = self.request
                        print("name:", thisname, "socket:", self.nameSockMap[thisname])
                        self.wfile.write("HELLO {}\n".format(thisname).encode("utf-8"))

            elif data[0] == "WHO":
                if len(data) > 1:
                    self.wfile.write("BAD-RQST-BODY\n".encode("utf-8"))
                else:
                    print("WHO-OK {}\n".format(','.join(self.nameSockMap.keys())))
                    self.wfile.write("WHO-OK {}\n".format(','.join(self.nameSockMap.keys())).encode("utf-8"))

            elif data[0] == "SEND":
                name = data[1]
                if name not in self.nameSockMap:
                    self.wfile.write("UNKNOWN\n".encode("utf-8"))
                else:
                    message = ' '.join(data[2:])

                    self.nameSockMap[name].sendall("DELIVERY {} {}\n".format(thisname, message).encode("utf-8"))
                    self.wfile.write("SEND-OK\n".encode("utf-8"))

            else:
                self.wfile.write("BAD-RQST-HDR\n".encode("utf-8"))


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = socketserver.ThreadingTCPServer((HOST, PORT), ClientHandler)
    print("Started server")
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
