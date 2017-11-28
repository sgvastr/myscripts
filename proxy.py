import socket
import sys
import threading
import time
import ssl
import os


create_ssl_cert_lock = threading.Lock()
def create_ssl_cert(domain):
    create_ssl_cert_lock.acquire()
    if not os.path.isfile("certs\\{0}.crt".format(domain)):
        try:
            os.system(
                "C:\\OpenSSL-Win32\\bin\\openssl.exe req -new -key certs\\server.key -out certs\\server.csr -subj /CN={0}".format(
                    domain))
            os.system(
                "C:\\OpenSSL-Win32\\bin\\openssl.exe ca -batch  -config C:\\OpenSSL-Win32\\bin\\san.cfg -policy signing_policy -extensions req_ext -out certs\\{0}.crt -infiles certs\\server.csr".format(
                    domain))
        finally:
            create_ssl_cert_lock.release()
    else:
        create_ssl_cert_lock.release()

class HttpsDecryptConnection:
    __client = None  # client socket
    __server = None  # server socket

    def __init__(self, client: socket):
        self.__client = client

    def __read_socket(self, socket: socket) -> bytearray:
        socket_data = bytearray()
        while 1:
            try:
                data = socket.recv(16384)
                if data:
                    socket_data.extend(data)
                else:
                    if not socket_data:
                        raise NameError("ConnectionClosed")
                    else:
                        break
            except BlockingIOError:
                break
            except ssl.SSLWantReadError:
                break
        return socket_data

    def __parse_http_header(self, http_request: bytearray) -> list:
        result = {}
        header_lines = http_request[:http_request.index(b"\r\n\r\n")].splitlines()
        first_line = header_lines[0].split(sep=b" ")
        result["Method"] = first_line[0].decode()
        result["Url"] = first_line[1].decode()
        result["Version"] = first_line[2].decode() if len(first_line) == 3 else ""

        del header_lines[0]  # удаляем первую строку из загаловка

        for line in header_lines:
            index = line.index(b":")
            method, value = line[:index], line[index + 2:]
            result[method.decode()] = value.decode()

        z = result["Host"].split(":")
        result["HostName"] = z[0]
        result["Port"] = int(z[1]) if len(z) == 2 else 80

        return result

    def process(self):
        if not self.__server:
            request = self.__client.recv(4096)

            if not request:
                raise NameError("ConnectionClosed")

            h = request.split(sep=b" ")[1].split(b":")
            host = h[0].decode()
            port = int(h[1].decode()) if len(h) == 2 else 80

            context = ssl.SSLContext()
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations("cacert.pem")

            self.__server = context.wrap_socket(socket.socket())
            self.__server.connect((host, port))
            self.__server.setblocking(0)

            cert = "certs\\{0}.crt".format(host)

            if not os.path.isfile(cert):
                        create_ssl_cert(host)

            self.__client.send(b"HTTP/1.0 200 Connection established\r\nProxy-agent: Proxy\r\n\r\n")
            self.__client = ssl.wrap_socket(self.__client, keyfile="certs\\server.key", certfile=cert, server_side=True)
            self.__client.setblocking(0)

        while 1:
            request = self.__read_socket(self.__client)
            if request:
                http_header = self.__parse_http_header(request)
                self.__server.sendall(request)
            time.sleep(1)
            response = self.__read_socket(self.__server)
            if response:
                self.__client.sendall(response)


    def __del__(self):
        self.__client.close()
        if self.__server:
            self.__server.close()


# *************************************************************
# *************************************************************
class HttpsConnection:
    __client = None
    __server = None
    __host = None

    def __init__(self, client: socket):
        self.__client = client
        self.__client.setblocking(0)

    def __tunnelling(self, src: socket, dst: socket):
        try:
            data = src.recv(16384)
            if data:
                dst.send(data)
            else:
                raise NameError("ConnectionClosed")
        except BlockingIOError:
            return

    def process(self):
        if not self.__server:
            request = self.__client.recv(4096)
            h = request.split(sep=b" ")[1].split(b":")
            host = h[0].decode()
            port = int(h[1].decode()) if len(h) == 2 else 80
            self.__server = socket.socket()
            self.__server.connect((host, port))
            self.__client.send(b"HTTP/1.0 200 Connection established\r\nProxy-agent: Proxy\r\n\r\n")
            self.__server.setblocking(0)
            self.__host = host+":"+str(port)

        self.__tunnelling(self.__client, self.__server)
        self.__tunnelling(self.__server, self.__client)

    def __del__(self):
        self.__client.close()
        if self.__server:
            self.__server.close()


# *************************************************************
# *************************************************************

class HttpConnection:
    __client = None  # client socket
    __server = None  # server socket

    def __init__(self, client: socket):
        self.__client = client
        self.__client.setblocking(0)

    def __read_socket(self, socket: socket) -> bytearray:
        socket_data = bytearray()
        while 1:
            try:
                data = socket.recv(16384)
                if data:
                    socket_data.extend(data)
                else:
                    if not socket_data:
                        raise NameError("ConnectionClosed")
                    else:
                        break
            except BlockingIOError:
                return socket_data
        return socket_data

    def __parse_http_header(self, http_request: bytearray) -> list:
        result = {}
        header_lines = http_request[:http_request.index(b"\r\n\r\n")].splitlines()
        first_line = header_lines[0].split(sep=b" ")
        result["Method"] = first_line[0].decode()
        result["Url"] = first_line[1].decode()
        result["Version"] = first_line[2].decode() if len(first_line) == 3 else ""

        del header_lines[0]  # удаляем первую строку из загаловка

        for line in header_lines:
            index = line.index(b":")
            method, value = line[:index], line[index + 2:]
            result[method.decode()] = value.decode()

        z = result["Host"].split(":")
        result["HostName"] = z[0]
        result["Port"] = int(z[1]) if len(z) == 2 else 80

        return result

    def __open_server(self, host: str, port: int):
        self.__server = socket.socket()
        self.__server.connect((host, port))
        self.__server.setblocking(0)

    def process(self):
        request = self.__read_socket(self.__client)
        if request:
            http_header = self.__parse_http_header(request)
            request = request.replace(("http://" + http_header["Host"]).encode(), b"", 1)
            self.__open_server(http_header["HostName"], http_header["Port"])
            self.__server.sendall(request)
            response = self.__read_socket(self.__server)
            while not response:
                time.sleep(0.5)
                response = self.__read_socket(self.__server)
            self.__client.sendall(response)
            self.__client.close()
            self.__server.close()
        else:
            self.__client.close()

    def __del__(self):
        self.__client.close()
        if self.__server:
            self.__server.close()


# *************************************************************
# *************************************************************

class ProxyServer:
    __https_connections = []

    def __https_handling(self):
        while 1:
            sc = self.__https_connections[:]
            for s in sc:
                try:
                    s.process()
                except:
                    #print(sys.exc_info())
                    s.__del__()
                    self.__https_connections.remove(s)
            time.sleep(0.05)

    def __http_handling(self, http_connection):
        try:
            http_connection.process()
        except NameError:
            http_connection.__del__()
        except:
            print(sys.exc_info())
            http_connection.__del__()


    def __start_http_proxy(self):
        sc = socket.socket()
        sc.bind(("", 1080))
        sc.listen(5)
        while 1:
            try:
                user_connection, addr = sc.accept()
                con = HttpConnection(user_connection)
                threading.Thread(target=self.__http_handling, args=(con,)).start()
            except:
                print("LISTENING HTTP", sys.exc_info())

    def __start_https_proxy(self):
        sc = socket.socket()
        sc.bind(("", 1081))
        sc.listen(5)
        threading.Thread(target=self.__https_handling).start()
        while 1:
            try:
                user_connection, addr = sc.accept()
                con = HttpsConnection(user_connection)
                self.__https_connections.append(con)
            except:
                print("LISTENING HTTPS", sys.exc_info())

    def __start_https_decrypt_proxy(self):
        sc = socket.socket()
        sc.bind(("", 1082))
        sc.listen(5)
        while 1:
            try:
                user_connection, addr = sc.accept()
                con = HttpsDecryptConnection(user_connection)
                threading.Thread(target=self.__http_handling, args=(con,)).start()
            except:
                print("LISTENING HTTP", sys.exc_info())

    def start(self):
        threading.Thread(target=self.__start_http_proxy).start()
        #threading.Thread(target=self.__start_https_proxy).start()
        threading.Thread(target=self.__start_https_decrypt_proxy).start()
        input("Press Enter to continue...")


proxy = ProxyServer()
proxy.start()
