from socket import *
import os
import sys
import codecs
import glob

PATH = os.path.abspath(os.getcwd())
path_list_file = PATH + "/archive_files.txt"

print(PATH)

archive_path_list = []

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            if not ".git" in fullPath and PATH in fullPath:
                fullPath = fullPath.replace(PATH, "")
                allFiles.append(fullPath)
                
    return allFiles

def get_archive_path_list(path_list_file):
    path_list_file = open(path_list_file, mode="r+")

    contents = path_list_file.readlines()

    for file_name in contents:
        file_name = file_name.replace("\n", "")
        if file_name != "":
            archive_path_list.append(file_name)

def find_files(filename, search_path):
    result = []

    # Wlaking top-down from the root
    for root, dir, files in os.walk(search_path):
        if filename in files:
            # gets the full path of the file found
            result_path = os.path.join(root, filename)

            if PATH in result_path:
                # cleans the path trimming it to be relative to the project folder
                filepath = result_path.replace(PATH, "")
                result.append(filepath)

    return result

def Server():
    archive_path_list = getListOfFiles(PATH)
    #get_archive_path_list(path_list_file)
    print(f"LIST OF PATHS => {archive_path_list}")

    HOST = ''
    PORT = 9000

    server_socket = socket(AF_INET, SOCK_STREAM)
    orig = (HOST, PORT)
    server_socket.bind(orig)
    server_socket.listen(1)

    try:
        while(1):
            (connectionSocket, addr) = server_socket.accept()
            pid = os.fork()

            if pid == 0:
                print("Cliente {} conectado ao servidor".format(addr))

                request = connectionSocket.recv(1024).decode()
                split_request = request.split()

                if split_request[0] == "GET":
                    params = split_request[1]

                    is_file_moved = False
                    if params in archive_path_list:
                        is_file_moved = True

                    file_path = PATH + params

                    try:
                        html_file = open(file_path, 'r')

                        data = "HTTP/1.1 200 OK\r\n"
                        data += "Content-Type: text/html; charset=utf-8\r\n"
                        data += "\r\n"
                        data += html_file.read()

                        connectionSocket.sendall(data.encode())
                        
                    except:
                        
                        if is_file_moved == True:
                            print("PARMS INSIDE")
                            data = "HTTP/1.1 301 FILE MOVED\r\n"
                            data += "Content-Type: text/html; charset=utf-8\r\n"
                            data += "\r\n"
                            data += "<html><head></head><body><h1>301 File moved</h1></body></html>"
                            connectionSocket.sendall(data.encode()) 
                        else:
                            data = "HTTP/1.1 404 NOT FOUND\r\n"
                            data += "Content-Type: text/html; charset=utf-8\r\n"
                            data += "\r\n"
                            data += "<html><head></head><body><h1>404 Not Found</h1></body></html>"
                            connectionSocket.sendall(data.encode())    

                elif split_request[0] == "POST":

                    # the vars sent by the POST request are on the last position
                    # of the split_request and if more than just a single variable
                    # they're sapareted by '&'
                    vars_list = split_request[-1]

                    if "&" in vars_list:
                        vars_list = vars_list.split('&')

                    post_vars_dict = {}

                    for var in vars_list:
                        name_and_value = var.split('=')
                        post_vars_dict[name_and_value[0]] = name_and_value[1]

                    data = "HTTP/1.1 200 OK\r\n"
                    data += "Content-Type: text/html; charset=utf-8\r\n"
                    data += "\r\n"
                    data += f"<html><head></head><body><h1>Dados capturados: {post_vars_dict['fname']} & {post_vars_dict['lname']}</h1></body></html>"
                    connectionSocket.sendall(data.encode()) 

                elif split_request[0] == "PUT":
                    params = split_request[1]

                    full_path = PATH + params

                    if os.path.exists(full_path):

                        archive_path_list.append(params)

                        data = "HTTP/1.1 201 CREATED\r\n"
                        data += "Content-Type: text/html; charset=utf-8\r\n"
                        data += "\r\n"
                        data += "<html><head></head><body><h1>201 CREATED</h1></body></html>"
                        connectionSocket.sendall(data.encode()) 
                    else:
                        data = "HTTP/1.1 404 NOT FOUND\r\n"
                        data += "Content-Type: text/html; charset=utf-8\r\n"
                        data += "\r\n"
                        data += "<html><head></head><body><h1>404 Not Found</h1></body></html>"
                        connectionSocket.sendall(data.encode()) 

                elif split_request[0] == "DELETE":
                    params = split_request[1]

                    full_path = PATH + params

                    if os.path.exists(full_path):
                        os.remove(full_path)

                        data = "HTTP/1.1 200 OK\r\n"
                        data += "Content-Type: text/html; charset=utf-8\r\n"
                        data += "\r\n"
                        data += "<html><head></head><body><h1>File Removed</h1></body></html>"
                        connectionSocket.sendall(data.encode()) 
                    else:
                        data = "HTTP/1.1 404 NOT FOUND\r\n"
                        data += "Content-Type: text/html; charset=utf-8\r\n"
                        data += "\r\n"
                        data += "<html><head></head><body><h1>404 Not Found</h1></body></html>"
                        connectionSocket.sendall(data.encode()) 

                else:
                    print("Comando não pode ser interpretado por esse servidor!")
                    data = "HTTP/1.1 400 Bad Request\r\n"
                    data += "Content-Type: text/html; charset=utf-8\r\n"
                    data += "\r\n"
                    data += "<html><head></head><body><h1>400 Bad Request</h1></body></html>"
                    connectionSocket.sendall(data.encode()) 
                    connectionSocket.close()
                    
                connectionSocket.close()
                sys.exit(0)
            else:
                connectionSocket.close()

    except KeyboardInterrupt:
        print("\n Shutting down... \n")
    except Exception as exc:
        print("Error: \n")
        print(exc)

print("Access http://localhost:9000")
Server()