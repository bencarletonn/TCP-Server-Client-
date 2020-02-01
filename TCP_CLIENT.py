import sys
import time
from socket import *

serverip = sys.argv[1]
port = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_STREAM) # create socket


try:
    clientSocket.connect((serverip, port)) # try to connect, if not print error
except OSError:
    print('Server is not running/unavailable')
    exit()

###############################

# recvall is a function that allows for the recieving of large amounts of data

def recvall(sock):
    BUFFER_SIZE = 4096
    global message_recieved
    message_recieved = ''
    while True:
        part = sock.recv(BUFFER_SIZE).decode()
        message_recieved += part
        if len(part) < BUFFER_SIZE:
            break
    return message_recieved

### CLIENT INSTRUCTIONS ###

print('\nInput POST_MESSAGE to send a message. You will be asked for the number of the board to post to, followed by the message title, content and finally a confirmation.')
print('\nInput GET_MESSAGES to recieve a list of the 100 most recent messages in the board. You will be asked the number of the board you would like to view.')
print('\nInput QUIT to exit the server.')
print('\nThe boards are shown below: ')

get_boards = 'GET_BOARDS'
clientSocket.send(get_boards.encode()) # immediately send a GET_BOARDS request to the server
get_boards = clientSocket.recv(1024).decode() # recieve reply to GET_BOARDS request 
print(get_boards)


while True:
    sentance = input(': ') 
    clientSocket.send(sentance.encode()) # send user input to the server
    try:
        clientSocket.settimeout(10) # set a time out of 10 seconds
        recvall(clientSocket) # recieve data from server in response to user input
        if message_recieved == 'Closing connection...': # if user has inputted QUIT 
            exit()
        print(message_recieved) # show response recieved from the server
    except timeout:
        print('ERROR: timed out')
        exit()
        

clientSocket.close() # close the socket if no longer connected
