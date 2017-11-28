import os
domain = "mail.ru"
os.system("C:\\OpenSSL-Win32\\bin\\openssl.exe req -new -key certs\\server.key -out certs\\server.csr -subj /CN={0}".format(domain))
os.system("C:\\OpenSSL-Win32\\bin\\openssl.exe ca -batch  -config C:\\OpenSSL-Win32\\bin\\san.cfg -policy signing_policy -extensions req_ext -out certs\\{0}.crt -infiles certs\\server.csr".format(domain))
