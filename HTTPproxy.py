"""HTTPproxy.py - Austin Poch - u1342727 - CS 4480 - PA1

This is a basic proxy server that parses requests from clients and
reconstructs them to be sent to a server. It listens for a response
from the server and once recieved passes it along back to the client. 

This script takes in 2 comand line arguments -a 'address to listen to' 
and -p 'port to listen to' if no arguments are given it defaults to
address "localhost" and port 2100.
"""

import signal
import sys
import re
import socket
import threading
from operator import index
from optparse import OptionParser

# Regex for headers
headerFormat = re.compile('^\\S+: .+$')

# Signal handler for pressing ctrl-c
def ctrl_c_pressed(signal, frame):
    sys.exit(0)

def sendAndRecieve_Server(data, serverHost, serverPort):
    """ 
    Sends 'data' to 'serveHost' at 'serverPort' 
    then returns a response from the server.

    :param data: string: The data being sent to the server.

    :return: string: The server's reply data.
    """

    # Send data to server  
    serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSkt.connect((serverHost, serverPort))
    print("Connected to server: " + serverHost + ":" + str(serverPort) + '\n')
    print(f'Sending to server:\n{data}')
    serverSkt.sendall(data.encode())

    # Recieve data from server
    serverReplyData = ''
    while True:
        data = serverSkt.recv(2048)
        serverReplyData += data.decode()
        if not data:
            break
    print(f'Recieved from server:\n{serverReplyData}')
    return serverReplyData

def getServerHost(data):
    """ 
    Extracts servers hostname from 'data'.

    :param data: list of strings: The request contining a hostname.

    :return: string: The server's hostname.
    """

    serverhost = ''
    serverhostandport = data[0].removeprefix('GET http://').split('/', 1)[0]
    if ':' in serverhostandport:
        serverhost = serverhostandport.split(':', 1)[0]
    elif ' ' in serverhostandport:
        serverhost = serverhostandport.split(' ', 1)[0]
    else:
        serverhost = serverhostandport
    return serverhost

def getServerPort(data):
    """ 
    Extracts server's port number from 'data'. Default to port 80.

    :param data: list of strings: The request which might contain a port number.

    :return: int: The server's port.
    """

    serverport = 80
    serverhostandport = data[0].removeprefix('GET http://').split('/', 1)[0]
    if ':' in serverhostandport:
        serverport = int(serverhostandport.split(':', 1)[1])
    return serverport

def getServerPath(data):
    """ 
    Extracts server's path from 'data'.

    :param data: list of strings: The request contining path.

    :return: string: The server's path.
    """

    path = data[0].removeprefix('GET http://').split(' ', 1)[0]
    if '/' in path:
        path = path[path.index('/'):]
    else:
        path = ''
    return path


def parseAndConstructRequest(data, path, serverHost):
    """ 
    Creates and returns a list of headers using 
    'path', 'serverHost' and any other heders in 'data'.

    :param data: list of strings: The full request.
    :param path: string: the path of the server.
    :param serverHost: string: Server hostname

    :return: string: Modified/updated delimited headers.
    """

    forwardData = []
    forwardData.append('GET ' + path + ' HTTP/1.0\r\n')
    forwardData.append('Host: ' + serverHost + '\r\n')

    # Remove unneeded lines from data
    data.pop(0)
    if len(data) > 0 and data[-1] == '':
        data.pop()
    if len(data) > 0 and data[-1] == '':
        data.pop()
 
    # Add aditional headers to forwardData
    for x in data:
        if headerFormat.match(x):
            if x != 'Connection: close' and x != 'Connection: keep-alive':
                forwardData.append(x + '\r\n')
        else:
            print("Recieved malformed header\n")
            forwardData.clear()
            forwardData.append('HTTP/1.0 400 Bad Request\r\n')
            break
    forwardData.append('Connection: close\r\n\r\n')
    return ''.join(forwardData)

def sendDataToClient(client, data):
    """ 
    Send encoded data to client and end connection

    :param client: The client socket
    :param data: string: The data to be sent.
    """

    print(f'Sending to client {threading.current_thread().ident}:\n{data}')
    client.sendall(data.encode())
    print('Sent!\n\nListening for new connections...\n')
    client.close()
 
def handle_client(clientSkt, clientAddress):
    """ 
    Recieves data from client and organizes it to be parsed. 
    Data is then reconstructed and sent to either the server or a
    bad/not implemented request sent client depending on request data.

    :param clientSkt: The client socket
    :param clientAddress: string: Client ip address.
    """

    print(f'Connection made from: {clientAddress}')

    # Recieve data with a buffer
    requestData = ''
    while True:
        data = clientSkt.recv(16)
        decodedData = data.decode()
        requestData += decodedData
        if requestData.endswith('\r\n\r\n') or requestData.endswith('\\r\\n\\r\\n'): 
            break 
    print(f'Recieved from client {threading.current_thread().ident}:\n{requestData}\n')

    # Fighting with autograder here
    data1 = requestData.split('\\r\\n')
    data2 = requestData.split('\r\n')
    if len(data1) > len(data2):
        requestData = data1
    else:
        requestData = data2

    # Remove empty list items 
    requestData.pop()
    requestData.pop()

    print('PARSING DATA!\n')
    #print(f'Data after split:\n{requestData}\n')

    # Handle GET requests
    if(requestData[0].startswith('GET http://') and (requestData[0].endswith('HTTP/1.0') or requestData[0].endswith('HTTP/1.0\r\n\r\n'))):
        
        #print("GET request!")

        serverHost = getServerHost(requestData)
        serverPort = getServerPort(requestData)
        path = getServerPath(requestData)

        #print(f'Request location:\nserverHost: {serverHost}\nserverPort: {serverPort}\npath: {path}\n')

        # Reconstruct request and respond to client
        if path == '':
            reconstructedData = 'HTTP/1.0 400 Bad Request\r\nConnection: close\r\n\r\n'
            sendDataToClient(clientSkt, reconstructedData)
        else:
            reconstructedData = parseAndConstructRequest(requestData, path, serverHost)
            serverReplyData = sendAndRecieve_Server(reconstructedData, serverHost, serverPort)
            sendDataToClient(clientSkt, serverReplyData)

    # Handle malformend/ non-GET requests 
    elif(requestData[0].startswith('HEAD http://') and (requestData[0].endswith('HTTP/1.0') or requestData[0].endswith('HTTP/1.0\r\n\r\n'))):
        print("HEAD request!\n")
        sendDataToClient(clientSkt, 'HTTP/1.0 501 Not Implemented')
    elif(requestData[0].startswith('POST http://') and (requestData[0].endswith('HTTP/1.0') or requestData[0].endswith('HTTP/1.0\r\n\r\n'))):
        print("POST request!\n")
        sendDataToClient(clientSkt, 'HTTP/1.0 501 Not Implemented')
    else:
        print("Recieved malformed request\n")
        sendDataToClient(clientSkt, 'HTTP/1.0 400 Bad Request')



# Start of program execution
# Parse out the command line server address and port number to listen to
parser = OptionParser()
parser.add_option('-p', type='int', dest='serverPort')
parser.add_option('-a', type='string', dest='serverAddress')
(options, args) = parser.parse_args()

# Setup correct server address and port
port = options.serverPort
address = options.serverAddress
if address is None:
    address = 'localhost'
if port is None:
    port = 2100

print('\nProxy server runnung on: ' + str(address) + ":" + str(port) + '\n')

# Set up signal handling (ctrl-c)
signal.signal(signal.SIGINT, ctrl_c_pressed)

# Set up primary listen socket
listeningSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listeningSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    listeningSkt.bind(('', port))
except:
    print('bind failed')
listeningSkt.listen(100)

# Handle new clients, each on their own thread.
while True:
    print('Listening for new connections...\n')
    (clientSkt, clientAddress) = listeningSkt.accept()

    thread = threading.Thread(target=handle_client, args=(clientSkt, clientAddress))
    thread.start()
    print(f'Active connections: {threading.active_count() - 1}\n')


    