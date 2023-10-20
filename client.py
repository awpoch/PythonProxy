# Place your imports here
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
    port = 2100

# Set up signal handling (ctrl-c)
signal.signal(signal.SIGINT, ctrl_c_pressed)

# Set up sockets to receive requests
clientSkt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSkt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

clientSkt.connect((address, port))
print("\nConnected to " + str(address) + ": " + str(port) + "\n")

message = input("input: ")
print(f'\nSending to server:\n{message}\n')
clientSkt.sendall(message.encode())

replyData = ''
while True:
    data = clientSkt.recv(16)
    replyData += data.decode()
    if not data:
        break
print(f'Recieved:\n{replyData}')
clientSkt.close()