#!usr/bin/env python
import socket, sys, thread
__author__ = 'Lucas Rondenet'
__email__ = 'lucasr@uoregon.edu'
__status__ = 'development'

SERVER_ADDRESS = ('localhost', 8080)
MAX_RECEIVE = 5000
QUEUE = 50


def main():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        # Create a tcp/ip socket...
        sock.bind(SERVER_ADDRESS)                                       # Associate socket with server address, being localhost...
        sock.listen(QUEUE)                                              # Put socket into server mode, waits for incoming connections

    except socket.error, (value, message):
        if sock:
            sock.close()
        print "Could not open socket: ", message
        sys.exit(1)

    while 1:
        connection, client_address = sock.accept()                                   # Returns socket to send/receive data and address bound to socket
        thread.start_new_thread(proxy, (connection, client_address, MAX_RECEIVE))    # Create new thread for connection...
    sock.close()                                                                     # Closes socket once done with proxy_thread


def proxy(connection, client_address, MAX_RECEIVE):
    request = connection.recv(MAX_RECEIVE)          # Receive data from browser by the socket (size 1024)...NEED TO CHANGE THIS LATER

    content_length_position = request.find("content-header")
    if content_length_position != -1:
        print "Found Content-Length header..."
        content_length_position = request.find("Content-Length")
        content_length = request[content_length_position+16:]
        content_length = content_length_position.split(" ")[0]
        MAX_RECEIVE = content_length

    first_line = request.split('\n')[0]             # Parse the first line
    url = first_line.split(' ')[1]                  # Get url from parsed first line

    print "This is the request... ", request        # Some debug statements to see what's going on...
    print "First Line", first_line
    print "URL: ", url

    # Find web server and port
    http_position = url.find("://")                 # Find position of "://"
    if (http_position == -1):                       # Can't find "://"
        temp = url
    else:
        temp = url[(http_position+3):]              # Get the rest of the url
    port_position = temp.find(":")                  # Find port if specified

    # Find path on web server
    webserver_position = temp.find("/")             # Find char index for first "/"
    if webserver_position == -1:                    # Can't find "/" uses length of temp
        webserver_position = len(temp)

    if port_position == -1 or webserver_position < port_position:       # Default port
        port = 80
        webserver = temp[:webserver_position]                           # Substring of temp
    else:
        print "Specific post request...."                               # For specific port request wasn't sure if this
                                                                        # was needed
    print "Connect to: ", webserver, port

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        # Create socket...
        sock.connect((webserver, port))                                 # Connect to webserver at port 80
        sock.send(request.encode())                                     # send encoded data through socket

        while 1:
            data = sock.recv(MAX_RECEIVE)
            if len(data) > 0:
                connection.send(data)
            else:
                break
        sock.close()
        connection.close()

    except socket.error, (value, message):
        if sock:
            sock.close()
        if connection:
            connection.close()
        print "Runtime Error: ", message
        sys.exit(1)

if __name__ == '__main__':
    main()
