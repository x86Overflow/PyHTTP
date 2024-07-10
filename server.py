import socket
import os
import datetime
import codes
import mimes
import config
import ssl
import threading

# Use config.py
GC_SERVERNAME = config.ServerName
GC_PORT = config.Port
GC_BIND = config.Bind
GC_WEBROOT = config.WebRoot
GC_VERSION = "1.4.0"
GC_CERT = config.CertPath
GC_KEY = config.KeyPath
GC_SSL = config.SSLEnable
GC_SSLPORT = config.SSLPort

# Create socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((GC_BIND, GC_PORT))
serversocket.listen(5)

if GC_SSL:
    sslsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sslsock.bind((GC_BIND, GC_SSLPORT))
    sslsock.listen(5)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(GC_CERT, GC_KEY)
    ssock = context.wrap_socket(sslsock, server_side=True)

# Get byte length of string
def utf8len(s):
    if type(s) is bytes: # Dont encode if it's already bytes
        return len(s)
    else :
        return len(s.encode('utf-8'))

# Convert headers to a dict
def decodeHeaders(headerArray):
    out = {}
    for header in headerArray:
        if ":" not in header: # Bad way of checking for a valid header
            continue
        split = header.split(": ")
        out[split[0]] = {
            "header": split[0],
            "data": split[1]
        }
    return out

# Function that creates the default PyHTTP headers
def writeHeaders(size, statusCode, statusString, mime):
    global GC_SERVERNAME, GC_VERSION, GC_BIND

    headers = f"""HTTP/1.1 {statusCode} {statusString}
Content-Length: {size}
Server: {GC_SERVERNAME} v{GC_VERSION}
Content-Type: {mime}
Host: {GC_BIND} 
Date: {datetime.datetime.utcnow().strftime("%a, %d-%m-%y %H:%M:%S")} GMT
Connection: close
"""
    return headers

def generateErrorPage(code, string):
    global GC_SERVERNAME

    page = f"""
<h1>{code} {string}</h1>
<hr>
<p><a href="https://github.com/breadtf/pyhttp">{GC_SERVERNAME} v{GC_VERSION}</a></p>
    """

    return page

def getRequestPath(headerArray):
    path = headerArray[0].split(" ")[1]
    if path.endswith("/"):
        path = path + "index.html"

    return path

def getFile(path, mime):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    return False

def getMethod(reqString):
    return reqString.split(" ")[0]

def sendErrorPage(con, statusCode, sendPage=True):
    errPage = generateErrorPage(statusCode, codes.codes[statusCode])
    headers = writeHeaders(utf8len(errPage), statusCode, codes.codes[statusCode], "text/html")

    if sendPage:
        con.send(str(headers + "\r\n" + errPage).encode())
    else:
        con.send(headers.encode() + "\r\n".encode())

    return True

def getMime(fileName):
    filename, file_extension = os.path.splitext(fileName)
    if file_extension in mimes.mimetypes:
        return mimes.mimetypes[file_extension]
    return "application/octet-stream"

def serveThread(sslEnable):
    while True:
        if sslEnable:
            try:
                con, addr = ssock.accept()
            except ssl.SSLError:
                continue
        else:
            con, addr = serversocket.accept()
        buf = con.recv(1024)
        # Define default status code
        statusCode = 200

        # Check if buffer is empty before attempting to respond
        if len(buf) > 0:

            # Hacky fix for sending https request to plain port
            try:
                # Raw header list
                rawHeaders = buf.decode().split("\r\n")
            except UnicodeDecodeError:
                con.close()
                continue

            reqPath = getRequestPath(rawHeaders)
            method = getMethod(rawHeaders[0])
            decodedHeaders = decodeHeaders(rawHeaders)
            if "User-Agent" in decodedHeaders:
                userAgent = decodedHeaders["User-Agent"]["data"]
            else:
                userAgent = "-"

            if method == "GET":
                # Serve 404 page if the requested file doesnt exist
                if not os.path.exists(GC_WEBROOT + reqPath):
                    statusCode = 404
                    sendErrorPage(con, 404, True)
                else:
                    mimetype = getMime(GC_WEBROOT + reqPath)
                    document = getFile(GC_WEBROOT + reqPath, mimetype)

                    if len(config.ExtDoc) != 0:
                        MGR_ExtState = "ExtDoc"
                        for ext in config.ExtDoc:
                            exec(open("extensions/" + ext).read())

                    headers = writeHeaders(utf8len(document), statusCode, codes.codes[statusCode], mimetype)

                    if len(config.ExtHead) != 0:
                        MGR_ExtState = "ExtHead"
                        for ext in config.ExtHead:
                            exec(open("extensions/" + ext).read())
                    headers = headers + "\r\n"

                    con.send(str(headers).encode()) # Send headers
                    con.send(document)
            elif method == "HEAD":
                if not os.path.exists(GC_WEBROOT + reqPath):
                    statusCode = 404
                    sendErrorPage(con, 404, False)
                else:
                    mimetype = getMime(GC_WEBROOT + reqPath)
                    document = getFile(GC_WEBROOT + reqPath, mimetype)
                    headers = writeHeaders(utf8len(document), statusCode, codes.codes[statusCode], mimetype)
                    con.send(str(headers).encode()) # Send headers
                    con.send("\r\n".encode())
                    # con.send(document)
            else:
                statusCode = 501
                sendErrorPage(con, 501, True)

            con.close() # Close the connection

            print(f"{addr[0]} - {method} {reqPath} - {statusCode} - \"{userAgent}\"")

if GC_SSL:
    sslThread = threading.Thread(target=serveThread, args=(True,))
    sslThread.start()
plainThread = threading.Thread(target=serveThread, args=(False,))
plainThread.start()

print(f"{GC_SERVERNAME} v{GC_VERSION} Started.")