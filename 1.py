import ssl
import socket
#domain = "mail.ru"
#os.system("C:\\OpenSSL-Win32\\bin\\openssl.exe req -new -key certs\\server.key -out certs\\server.csr -subj /CN={0}".format(domain))
#os.system("C:\\OpenSSL-Win32\\bin\\openssl.exe ca -batch  -config C:\\OpenSSL-Win32\\bin\\san.cfg -policy signing_policy -extensions req_ext -out certs\\{0}.crt -infiles certs\\server.csr".format(domain))
print(ssl.OPENSSL_VERSION)
print(ssl.HAS_SNI)
context = ssl.SSLContext()
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations("cacert.pem")

__server = context.wrap_socket(socket.socket(), server_hostname="anti-malware.ru")
__server.connect(("anti-malware.ru", 443))