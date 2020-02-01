import sys
import time
import os
from socket import *
import _thread


######## SERVER MANUAL ########
# 
# 1. If a client inputs GET_BOARDS, they will recieve a list of the message boards  
# 2. If a client inputs POST_MESSAGE, they will be prompted of the message board they would like to send the message, aswell as the title, the content, and to POST_MSG to confirm 
# 3. If a client inputs GET_MESSAGES, they will be prompted of the message board they would like to get the messages for, and the first 100 messages will be displayed
# 3. If a client inputs QUIT, they will be disconnected from the server
# 4. The server log logs all information the client enters, and whether it was 'OK' or produced an 'ERROR'. It also displays the time the message was recieved. 


######## SERVER #########

### LIST OF SERVER FUNCTIONS ###

##########################################################################

# Simple function for recieving large amounts of data

def recvall(sock):
    BUFFER_SIZE = 4096
    global message_content
    message_content = ''
    while True:
        part = sock.recv(BUFFER_SIZE).decode()
        message_content += part
        if len(part) < BUFFER_SIZE:
            break
    return message_content

##########################################################################

#1 This function sends a list of the available message boards to the user 

def sendclientBoards(clientSocket):
    global boards
    boards = os.listdir('board') # assign list of message boards to 'boards' variable 
    list_board = '\n' 

    for i in range(len(boards)):
        boards_edited = '{}.\t{}\n'.format(i+1, boards[i]) # prints boards in a list
        list_board += boards_edited

    list_board = list_board.replace(' ', '_') # remove spaces in message board titles with '_'
    print('Sending boards to client...')
    clientSocket.sendall(list_board.encode()) # send message boards to the client in a numbered list

##############################################################################

#2 This function posts messages into the specified message board

def post(clientSocket):
    comment_1 = 'Please enter the number of a specified board'
    clientSocket.send(comment_1.encode()) # ask the client for which board they would like to post to
    num_board = clientSocket.recv(1024).decode() # recieve the number relating to which board they would like to post to

    comment_2 = 'Please enter a message title'
    clientSocket.send(comment_2.encode()) # ask the client for the message title
    message_title = time.strftime('%Y%m%d-%H%M%S-') + clientSocket.recv(1024).decode() # recieve the message title and add the time/date it was recieved
    message_title = message_title.replace(' ', '_') 

    comment_3 = 'Please enter message content'
    clientSocket.send(comment_3.encode()) # ask the client for the message content 
    #message_content = clientSocket.recv(1024).decode() # recieve the message content ############
    recvall(clientSocket)

    comment_4 = 'Enter POST_MSG to confirm'
    clientSocket.send(comment_4.encode()) # ask for confirmation
    post_msg = clientSocket.recv(1024).decode() # recieve confirmation
    if post_msg != 'POST_MSG': # if recieved message isnt confirmation, ask once more again, else cancel the message
        error = comment_4 + '. Failing again will cancel the message'
        clientSocket.send(error.encode())
        post_msg = clientSocket.recv(1024).decode()
        if post_msg != 'POST_MSG':
            error = 'Cancelling message...'
            clientSocket.send(error.encode())
            return 
    
    global boards
    os.chdir(os.getcwd() + '/board' + '/' + boards[int(num_board)-1]) # enter directory of board num_board (the board the client specified)

    f = open('{}'.format(message_title + '.txt'), 'w+') # create a folder in the directory with title message_title
    f.write('{}'.format(message_content)) # write message_content in file
    f.close()

    os.chdir('..') # return back to original directory
    os.chdir('..') 

    confirm = 'Your message has been sent and recieved!'
    clientSocket.send(confirm.encode())

    return

#####################################################################################

#3 this function closes the client socket 

def closeConnection(clientSocket):
    closing_connection = 'Closing connection...'
    print(closing_connection, 'with ', address)
    clientSocket.send(closing_connection.encode()) # tell client closing connection
    clientSocket.close() # close connection

#####################################################################################

#4 this function requests the 100 most recent messages from a specified board
    
def newrequestList(x, clientSocket):
    message_list = ''
    boards = os.listdir('board')
    os.chdir(os.getcwd() + '/board' + '/' + boards[x-1]) # change directory to board client specified
    messages = os.listdir() 
    if len(messages) == 0:
        warning = '\tThis board is empty\n' # if message board is empty, tell client 
        clientSocket.send(warning.encode())
        os.chdir('..') # change back to original directory
        os.chdir('..')
        return 
    if len(messages) < 100: # 100 most recent messages
        for i in range(len(messages)):
            f = open(messages[i], 'r') # open each message
            messages_edited = '{}.\t{} - {}\n'.format(i+1, messages[i], f.read()) # format using number, title, content
            message_list += messages_edited
        f.close()
        clientSocket.sendall(message_list.encode()) # send 100 most recent messages      
    else:
        for i in range(100): # if there is more than 100 messages
            f = open(messages[i], 'r')
            messages_edited = '{}.\t{} - {}\n'.format(i+1, messages[i], f.read()) 
            message_list += messages_edited
        f.close() 
        clientSocket.sendall(message_list.encode())

    os.chdir('..') # change back to original directory 
    os.chdir('..')

######################################################################################

# Server code 

def connect(clientSocket, address):

    print('Connection from {}!'.format(address))

    while True:
        data = clientSocket.recv(1024).decode() # recieve data from client

        if data == 'GET_BOARDS': # if data is GET_BOARDS send the client the boards
            try:
                sendclientBoards(clientSocket)
                f = open('server.log.txt', 'a') # log OK for GET_BOARDS
                f.write('\n{}\t\t{}\tGET_BOARDS\t\tOK'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y')))
                f.close()
            except OSError:
                error = 'ERROR'
                clientSocket.send(error.encode())
                f = open('server.log.txt', 'a') # log ERROR for GET_BOARDS
                f.write('\n{}\t\t{}\tGET_BOARDS\t\tError'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y')))
                f.close()
                      
                
        elif data == 'POST_MESSAGE': # if data is POST_MESSAGE prompt the client to post a message
            try:
                post(clientSocket)
                f = open('server.log.txt', 'a') # log OK for POST_MESSAGE
                f.write('\n{}\t\t{}\tPOST_MESSAGE\t\tOK'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y')))
                f.close()
            except IndexError:
                error = 'ERROR: specified board does not exist!'
                clientSocket.send(error.encode())
                f = open('server.log.txt', 'a') # log ERROR for POST_MESSAGE
                f.write('\n{}\t\t{}\tPOST_MESSAGE\t\tError'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y')))
                f.close()
            except ValueError:
                error = 'ERROR: specified board does not exist!'
                clientSocket.send(error.encode())
                f = open('server.log.txt', 'a') # log ERROR for POST_MESSAGE
                f.write('\n{}\t\t{}\tPOST_MESSAGE\t\tError'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y')))
                f.close()
                
                
            
        elif data == 'QUIT': # if data is QUIT close the socket 
            closeConnection(clientSocket)
            f = open('server.log.txt', 'a') # log OK for QUIT
            f.write('\n{}\t\t{}\tQUIT\t\tOK'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y')))
            f.close()
            break

        
        elif data == 'GET_MESSAGES': # if data is GET_MESSAGES send 100 most recent messages from specified board 
            specify = 'Specify a board: '
            clientSocket.send(specify.encode())
            try:
                board_num = clientSocket.recv(1024)
            except ConnectionAbortedError:
                break
            try:
                newrequestList(int(board_num), clientSocket)
                f = open('server.log.txt', 'a') # log OK for GET_MESSAGES
                f.write('\n{}\t\t{}\tGET_MESSAGES({})\t\tOK'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y'), int(board_num)))
                f.close()
            except IndexError:
                error = 'ERROR: specified board does not exist!'
                clientSocket.send(error.encode())
                f = open('server.log.txt', 'a') # log ERROR for GET_MESSAGES
                f.write('\n{}\t\t{}\tGET_MESSAGES({})\t\tError'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y'), int(board_num)))
                f.close()
            except ValueError:
                error = 'ERROR: Please enter the number of a valid board!'
                clientSocket.send(error.encode())
                f = open('server.log.txt', 'a') # log ERROR for GET_MESSAGES
                f.write('\n{}\t\t{}\tGET_MESSAGES({})\t\tError'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y'), board_num))
                f.close()

            
        else:
            invalid_command = 'You have entered an invalid command, please try again!'
            clientSocket.send(invalid_command.encode())
            f = open('server.log.txt', 'a') # log ERROR for some invalid message
            f.write('\n{}\t\t{}\tINVALID_MSG\t\tError'.format(address[0] + ':' + str(address[1]), time.strftime('%a %d %b %H:%M:%S %Y')))
            f.close()


serverip = sys.argv[1] 
port = int(sys.argv[2])
serverSocket = socket(AF_INET, SOCK_STREAM) # create a socket
try:
    boards = os.listdir('board') 
    if boards == []:
        print('No message boards defined')
        exit()
        
except FileNotFoundError:
    print('board folder does not exist')
    exit()
    
    
try:
    serverSocket.bind((serverip, port))
except OSError:
    print('Server unavailable')
    exit()

serverSocket.listen(5)
print('The server is ready to recieve communications')

while True:
    clientSocket, address = serverSocket.accept()
    _thread.start_new_thread(connect, (clientSocket, address))

