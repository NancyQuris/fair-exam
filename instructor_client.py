from ftplib import FTP
import os.path
import socket
import time
import setting
import threading
import struct
import pickle
import cv2

def ftp_command_handling():
    # instructor client
    # Func 1: create a folder in ftp server
    # Func 2: upload exam question file to the folder
    # Func 3: download student's answer file from the folder
    print("File Transfer Client Start.")
    print("Available command: mkdir, upload, download, exit")
    while True:
        cmd = input("Please enter the command: ")
        print("command = {}".format(cmd))
        if cmd == "mkdir":
            makeDirectory()
        elif cmd == "upload":
            uploadFile()
        elif cmd == "download":
            downloadFile()
        elif cmd == "exit":
            print("Program Exited.")
            break
        else:
            print("Invalid command.")
            print("Available command: mkdir, upload, download, exit")


def exam_start():
    print("Prepare for exam")
    makeAnswerDirectory()
    print("preparation done, ready to start exam")
    stream = threading.Thread(target=streaming)
    stream.start()
    net_stat = threading.Thread(target=netstat)
    net_stat.start()
    # when exam ends, force to upload file
    stream.join()
    net_stat.join()
    print("Exam finished")


def makeAnswerDirectory():
    print("------------ Create directory ------------")
    print("Building connection to the ftp server...")
    ftp = FTP()
    ftp.connect(setting.ftp_server_host, setting.ftp_instructor_server_port)
    print("Connected the ftp server.")
    user = input("Please enter the username: ")
    password = input("Please enter the password: ")
    ftp.login(user=user, passwd=password)
    print("Logged in successfully")
    ftp.mkd(setting.student_answer_directory)
    print(setting.student_answer_directory, "created.")
    ftp.quit()
    print("------------ Directory Creation Finished------------")


def makeDirectory():
    print("------------ Create directory ------------")
    print("Building connection to the ftp server...")
    ftp = FTP()
    ftp.connect(setting.ftp_server_host, setting.ftp_instructor_server_port)
    print("Connected the ftp server.")
    user = input("Please enter the username: ")
    password = input("Please enter the password: ")
    ftp.login(user=user, passwd=password)
    print("Logged in successfully")
    dir_name = input("Please enter the name of folder you want to create: ")
    ftp.mkd(dir_name)
    print(dir_name, "created.")
    ftp.quit()
    print("------------ Directory Creation Finished------------")


def uploadFile():
    print("------------ Upload file ------------")
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
    else:
        print("Folder not found, please create the directory first. If you have created the directory, please check the directory name entered.")
        ftp.quit()
        exit(1)

    filepath = input("Please enter the local path of the file you want to upload to server: ")
    if not os.path.isfile(filepath):
        print("Entered file not found.")
        exit(1)
    filename = input("Please name the file in the server: ")

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
    video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_socket.connect((setting.streaming_server_host, setting.streaming_instructor_server_port))

    data = b''
    payload_size = struct.calcsize("L")
    while True:
        while len(data) < payload_size:
            data += video_socket.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += video_socket.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame = pickle.loads(frame_data)
        cv2.imshow('frame', frame)


def netstat():
    netstat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    netstat_socket.connect((setting.net_socket_server_host, setting.net_socket_instructor_server_port))
    while True:
        data = netstat_socket.recv(1024)
        print(data.decode('utf-8'))
        if not data:
            break

    netstat_socket.close()


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
