from ftplib import FTP
import psutil
import time
import socket
import setting
import threading
import cv2
import numpy as np
import socket
import sys
import pickle
import struct
import os


def ftp_command_handling():
    # instructor client
    # Func 1: download exam question file from the folder
    # Func 2: upload exam answer file to the folder
    print("File Transfer Client Start.")
    print("Available command: download, exit")
    while True:
        cmd = input("Please enter the command: ")
        print("command = {}".format(cmd))
        if cmd == "download":
            downloadFile()
        elif cmd == "exit":
            print("Program Exited.")
            break
        else:
            print("Invalid command.")
            print("Available command: download, exit")


def exam_start():
    print('Exam is about to start, please input required infomation')
    user = input("Please enter the username: ")
    password = input("Please enter the password: ")
    filepath = input("Please enter the local path of the file you want to upload to server: ")
    filename = input("Please name the file in the server: ")

    stream = threading.Thread(target=streaming)
    stream.start()
    net_stat = threading.Thread(target=netstat)
    net_stat.start()
    # when exam ends, force to upload file
    stream.join()
    net_stat.join()
    print("Exam finished, file uploading")
    uploadFile(user, password, filepath, filename)


def uploadFile(user, password, filepath, filename):
    print("------------ Upload file ------------")
    print("Building connection to the ftp server...")
    ftp = FTP()
    ftp.connect(setting.ftp_server_host, setting.ftp_instructor_server_port)
    print("Connected the ftp server.")
    # user = input("Please enter the username: ")
    # password = input("Please enter the password: ")
    ftp.login(user=user, passwd=password)
    print("Logged in successfully")

    dir_name = setting.student_answer_directory
    if dir_name in ftp.nlst():
        # change to the directory of the exam folder
        ftp.cwd(dir_name)
        print("Current directory:", ftp.pwd())
    else:
        print("Folder not found, please create the directory first. If you have created the directory, please check the directory name entered.")
        ftp.quit()
        exit(1)

    # filepath = input("Please enter the local path of the file you want to upload to server: ")
    if not os.path.isfile(filepath):
        print("Entered file not found.")
        exit(1)
    # filename = input("Please name the file in the server: ")

    file = open(filepath, 'rb')
    ftp.storbinary('STOR '+filename, file)
    file.close()
    print("File uploaded successfully")
    ftp.quit()
    print("------------ File Upload Finished------------")


def downloadFile():
    print("------------ Download file ------------")
    print("Building connection to the ftp server...")
    ftp = FTP()
    ftp.connect(setting.ftp_server_host, setting.ftp_instructor_server_port)
    print("Connected the ftp server.")
    user = input("Please enter the username: ")
    password = input("Please enter the password: ")
    ftp.login(user=user, passwd=password)
    print("Logged in successfully")

    dir_name = input("Please enter the name of folder you want to go to: ")
    if dir_name in ftp.nlst():
        # change to the directory of the exam folder
        ftp.cwd(dir_name)
        print("Current directory:", ftp.pwd())
    else :
        print("Folder not found, please create the directory first. If you have created the directory, please check the directory name entered.")
        ftp.quit()
        exit(1)

    filename = input("Please enter the name of file you want to download: ")
    if filename not in ftp.nlst():
        print("File not found.")
        exit(1)
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    ftp.quit()
    localfile.close()
    print("------------ File Download Finished------------")


def streaming():
    start_time = time.time()
    cap = cv2.VideoCapture(0)
    video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_socket.connect((setting.streaming_server_host, setting.streaming_student_server_port))
    while True:
        ret, frame = cap.read()
        data = pickle.dumps(frame)
        video_socket.sendall(struct.pack("L", len(data)) + data)
        if time.time() - start_time > setting.total_exam_time:
            break
    video_socket.close()


def netstat():
    connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection_socket.connect((setting.net_socket_server_host, setting.net_socket_student_server_port))

    remote_ips = set()
    sockets = psutil.net_connections(kind='all')
    num_of_socks = len(sockets)
    for s in sockets:
        remote_ips.add(s.raddr)

    str1 = '**************BEGINNING STATISTICS*****************\n'
    connection_socket.sendall(str1.encode('utf-8'))
    str2 = 'number of sockets connections: ' + str(num_of_socks) + '\n'
    connection_socket.sendall(str2.encode('utf-8'))
    # print(remote_ips)
    step = 1
    sleep_time = setting.time_to_send  # in second
    while step * sleep_time <= setting.total_exam_time:
        time.sleep(sleep_time)  # check statistics in every 2 minutes
        current_sockets = psutil.net_connections(kind='all')
        new_connection = set()
        for current_s in current_sockets:
            remote_ip = current_s.raddr
            if remote_ip in remote_ips:
                continue
            else:
                ip = remote_ip.ip
                port = remote_ip.port
                try:
                    addr = socket.gethostbyaddr(ip)
                    new_connection.add((addr[0], ip, port))
                except socket.herror:
                    new_connection.add(remote_ip)
                    pass

        str3 = '**************TIME=' + str(step * sleep_time/60) + ' min STATISTICS*****************\n'
        connection_socket.sendall(str3.encode('utf-8'))
        str4 = 'number of sockets connections: ' + str(len(current_sockets)) + '\n'
        connection_socket.sendall(str4.encode('utf-8'))
        if len(new_connection) == 0:
            str5 = 'no new connection found\n'
            connection_socket.sendall(str5.encode('utf-8'))
        else:
            str6 = 'new connections not found in at the beginning:\n'
            connection_socket.sendall(str6.encode('utf-8'))
            for c in new_connection:
                str7 = str(c) + '\n'
                connection_socket.sendall(str7.encode('utf-8'))

        step += 1

    connection_socket.close()


if __name__ == '__main__':
    print('select mode: U to upload or download file, E to start exam, exit to stop the program')
    while True:
        command = input("Please enter the command: ")
        if command == 'U':
            ftp_command_handling()
        elif command == 'E':
            exam_start()
        elif command == 'exit':
            print("Goodbye")
            exit(1)
        else:
            print("Invalid command.")
            print("Available command: U, E, exit")
