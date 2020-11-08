import os
import socket
import time
import setting
import sys
import cv2
import pickle
import numpy as np
import struct
import threading


def start():
    stream = threading.Thread(target=streaming)
    stream.start()
    net_stat = threading.Thread(target=netstat)
    net_stat.start()
    # when exam ends, force to upload file
    stream.join()
    net_stat.join()


def streaming():
    streaming_instructor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    streaming_instructor_socket.bind((setting.streaming_server_host, setting.streaming_instructor_server_port))
    streaming_instructor_socket.listen(1)
    instructor_conn, instructor_addr = streaming_instructor_socket.accept()

    streaming_student_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    streaming_student_socket.bind((setting.streaming_server_host, setting.streaming_student_server_port))
    streaming_student_socket.listen(1)

    conn, addr = streaming_student_socket.accept()

    while True:
        data = conn.recv(4096)
        if not data:
            break
        instructor_conn.sendall(data)

    streaming_instructor_socket.close()
    streaming_student_socket.close()


def netstat():
    net_socket_instructor_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    net_socket_instructor_server.bind((setting.net_socket_server_host, setting.net_socket_instructor_server_port))
    net_socket_instructor_server.listen(1)
    connection, address = net_socket_instructor_server.accept()

    net_socket_student_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    net_socket_student_server.bind((setting.net_socket_server_host, setting.net_socket_student_server_port))
    net_socket_student_server.listen(1)
    conn, addr = net_socket_student_server.accept()

    while True:
        data = conn.recv(1024)
        if not data:
            break
        connection.sendall(data)

    net_socket_student_server.close()
    net_socket_instructor_server.close()


if __name__ == '__main__':
    start()
