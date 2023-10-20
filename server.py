import signal
import sys
import socket
from optparse import OptionParser

# Signal handler for pressing ctrl-c
def ctrl_c_pressed(signal, frame):
    sys.exit(0)

# Start of program execution
# Parse out the command line server address and port number to listen to
parser = OptionParser()
parser.add_option('-p', type='int', dest='serverPort')
parser.add_option('-a', type='string', dest='serverAddress')
(options, args) = parser.parse_args()

port = options.serverPort
address = options.serverAddress
if address is None:
    address = 'localhost'
if port is None:
    port = 2101

print('\nReflection server running on: ' + str(address) + ":" + str(port) + '\n')

# Set up signal handling (ctrl-c)
signal.signal(signal.SIGINT, ctrl_c_pressed)

# Set up sockets to receive requests
serverSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    serverSkt.bind((address, port))
except:
    print('bind failed\n')
serverSkt.listen(5)

while True:
    print('Listening for new connections...\n')
    (clientSkt, clientAddress) = serverSkt.accept()
    print(f'Connection made from: {clientAddress}\n')
    requestData = ''
    while True:
        data = clientSkt.recv(16)
        decodedData = data.decode()
        requestData += decodedData
        if requestData.endswith('\r\n\r\n'): 
            break    
    print(f'Recieved from client:\n{requestData}')
    print(f'Sending to client:\n{requestData}')
    clientSkt.sendall(requestData.encode())
    print('Sent!\n')
    clientSkt.close()