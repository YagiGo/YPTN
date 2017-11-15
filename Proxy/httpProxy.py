#! /usr/bin/env python
import socket, sys
from _thread import *
'''
try:
    listening_port = input("[*]Enter Listening Port Number:")
except KeyboardInterrupt:
    print("[*] Keyboard Interrupt, Exiting...")
    sys.exit()
'''
max_conn = 5 # Max Connection Allowed
buffer_size = 8192 # Max Socket Buffer Size=8k

def initSocket():
    try:
        listening_port = int(input("[*]Enter Listening Port Number:"))
    except KeyboardInterrupt:
        print("[*] Keyboard Interrupt, Exiting...")
        sys.exit()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('',listening_port)) #bind socket
        s.listen(max_conn) # Listening for Incoming Connections
        print("[*] Initializing Sockets...Done")
        print("[*] Sockets Binded Successfully")
        print("[*] Server started at [%d]" %listening_port)
    except Exception as e:
        print("ERROR:" + str(e))
        print("[*] Unable to Initialize")
        sys.exit(2)
    while (1):
        try:
            conn, addr = s.accept()
            data = conn.recv(buffer_size)
            # print(conn)
            # print(addr)
            # print(data)
            #start_new_thread(conn_string,(conn,data,addr))
            start_new_thread(conn_string, (conn,data,addr))
            # print(1)
        except KeyboardInterrupt:
            print("User Interrupt, server shutting Down")
            sys.exit(1)
            s.close()
    s.close()
def conn_string(conn, data, addr):
    # print(data)
    first_line = (data.split(b'\n')[0]) # Get First Line
    # print(first_line)
    url = first_line.split(b' ')[1] # Get URL
    # print(url)
    http_pos = (url.find(b"://")) # Get rid of http:// or https://
    # print(http_pos)
    if(http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos+3):] # find the url
    # print(temp)
    port_pos = (temp.find(b":")) # Find the port, if any
    webserver_pos = (temp.find(b'/')) # Find the server
    if(webserver_pos == -1):
        webserver_pos = len(temp)
    if(port_pos == -1 or webserver_pos < port_pos):
        # Default Port 80
        port = 80
        webserver = temp[:webserver_pos]
    else:
        # Other ports than 80
        port = int((temp[(port_pos + 1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]
    # print("Webserver: " + str(webserver))
    # print("Port Number: " + str(port))
    proxy_server(webserver, port, conn, data,addr )
def proxy_server(webserver, port, conn, data, addr):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver,port))
        print(data)
        s.send(data)

        while(1):
            reply = s.recv(buffer_size)
            # print(reply)
            # print("PROXY WORKING!")
            if(len(reply) > 0):
                # Get data back from web server
                conn.send(reply) # Send reply back to client
                # There is someting you should do
                #TODO Something Related to Optimization
                dar = float(len(reply))
                dar = float(dar/1024)
                dar = "%.3s" %(str(dar))
                dar = "%s KB" % (dar)
                # Calculate Size of the Reply
                print("[*] Request Done:%s=>%s<=" %(str(addr[0]), str(dar)))
            else:
                # print("Nothing Returned!")
                # Nothing Returned from Web Server
                break
    except Exception as e:
        print(e)
        s.close()
        conn.close()
        sys.exit(1)

def demoProxy():
    initSocket()
demoProxy()