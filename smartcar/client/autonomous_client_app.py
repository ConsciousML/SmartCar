#!/usr/bin/env python
# -*- coding: utf-8 -*-
from socket import * 
import numpy
import cv2
import os
import pickle
import scipy
import filters
from sklearn.multiclass import OneVsRestClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import PIL

"""

This file contains the code for the client i.e the deviced connected
to the remote-controlled car. It defined all the function to send
action messages to the server i.e the remote controlled car.


"""


os.system('xset r off')
ctrl_cmd = ['forward', 'backward', 'left', 'right', 'stop', 'read cpu_temp', 'home', 'distance', 'x+', 'x-', 'y+', 'y-', 'xy_home']

HOST = '192.168.43.46'
HOST = '172.20.10.11'
PORT = 21567
BUFSIZ = 1024             # buffer size
ADDR = (HOST, PORT)

tcpCliSock = socket(AF_INET, SOCK_STREAM)   # Create a socket
tcpCliSock.connect(ADDR)                    # Connect with the server
tcpCliSock.setblocking(1)

dira = 0

dic_dir = {-1: "left", 0: "forward", 1: "right"}
dic_dir_l = {1: "left", 0: "home", 2: "right"}
clf = joblib.load("../forest_defaultparams.joblib.pkl")


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def get_img():
    length = recvall(tcpCliSock, 16)
    stringData = recvall(tcpCliSock, int(length))
    img = numpy.fromstring(stringData, dtype='uint8')
    imgdec = cv2.imdecode(img, 1)
    return imgdec

def process_dir(dir):
    print dir
    tcpCliSock.send(dir)
    get_img(dir)

# =============================================================================
# The function is to send the command forward to the server, so as to make the
# car move forward.
# =============================================================================
def forward_fun(event):
    process_dir("forward")

def backward_fun(event):
    process_dir("backward")

def left_fun(event):
    global dira
    dira = -1
    process_dir("left")

def right_fun(event):
    global dira
    dira = 1
    process_dir("right")

def stop_fun(event):
    process_dir('stop')

def home_fun(event):
    global dira
    dira = 0
    process_dir('home')

def x_increase(event):
    process_dir('x+')

def x_decrease(event):
    process_dir('x-')

def y_increase(event):
    process_dir('y+')

def y_decrease(event):
    process_dir('y-')

def xy_home(event):
    process_dir('xy_home')

spd = 35

def changeSpeed():
    tmp = 'speed'
    global spd
    data = tmp + str(spd)  # Change the integers into strings and combine them with the string 'speed'.
    print 'sendData = %s' % data
    tcpCliSock.send(data)  # Send the speed data to the server(Raspberry Pi)


def main():
    tcpCliSock.send("OK")
    get_img()
    changeSpeed()

    rep = tcpCliSock.recv(64)

    tcpCliSock.send("OK")
    get_img()
    tcpCliSock.send("forward")


    tcpCliSock.recv(64)

    while True:
        tcpCliSock.send("OK")
        img = get_img()
        img = PIL.Image.fromarray(numpy.uint8(img))

        img = img.convert('L') # 'L' is monochrome, '1' is black and white
        img = numpy.array(img)

        img = filters.bin_array(img, 160)
        img = scipy.misc.imresize(img, (80, 60), interp="nearest")
        img = img.reshape((1,60*80))

        data = dic_dir_l[clf.predict(img)[0]]
        tcpCliSock.send(data)

        tcpCliSock.recv(64)

if __name__ == '__main__':
	main()
