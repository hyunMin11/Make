__author__ = 'hyun'

import socket, sys, thread

#declare
MAX_RECEIVE = 5000      #max len of data    
QUEUE = 1000    #max thread
SERVER_ADDRESS = ('localhost', 8080)        #proxy server

def main():
    try:        #make socket at port 8080
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
        sock.bind(SERVER_ADDRESS)                                       
        sock.listen(QUEUE)                                              

    except socket.error, (value, message):
        sock.close()
        print "unconnected ", message
        sys.exit(1)

    while 1:        #accept client
        connection, client_address = sock.accept()                                   
        thread.start_new_thread(proxy, (connection, MAX_RECEIVE))       #make thread  
    sock.close()                                                                     


def proxy(connection,  MAX_RECEIVE):        # function that make socket to server
    request = connection.recv(MAX_RECEIVE)         #get data to client  

    first_line = request.split('\n')[0]         #get url to data         
    url = first_line.split(' ')[1]                 

    print "Request :" , first_line

    http_pos = url.find("://")                 
    if (http_pos == -1):                       
        temp = url
    else:
        temp = url[(http_pos+3):]              
    port_pos = temp.find(":")                  

    webserver_pos = temp.find("/")             
    if webserver_pos == -1:                    
        webserver_pos = len(temp)

    if port_pos == -1 or webserver_pos < port_pos:       
        port = 80
        webserver = temp[:webserver_pos]                           


    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        #make socket (url , 80)      
        sock.connect((webserver, port))                                 
        sock.send(request)                                     

        while 1:
            data = sock.recv(MAX_RECEIVE)           #recieve data from server
            if len(data) > 0:
                connection.send(data)
            else:
                break
        sock.close()
        connection.close()              #end connection

    except socket.error, (value, message):
        sock.close()
        connection.close()
        print "Runtime Error: ", message
        sys.exit(1)

if __name__ == '__main__':
    main()
