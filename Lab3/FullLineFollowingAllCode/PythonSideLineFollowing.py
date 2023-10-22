#!/usr/bin/env python3
import serial
from time import sleep
import numpy as np
from sendStringScript import sendString
from sys import exit
import time

leftMotor=int(100)
rightMotor=int(100)
state = 1
lines_hit = 0
z = 3500
incomingData = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
intersectionTimer = 0
lineHit = False

def setup():
    global ser
    ser=serial.Serial('/dev/ttyACM0',115200)
    ser.reset_input_buffer() #clears anything the arduino has been sending while the Rpi isnt prepared to recieve.

def main():
    while(True):
        global state
        print(str(leftMotor), str(rightMotor))
        print(state)
        print(lines_hit)
        #print(incomingData)
        if (state == 1):
            moveForward()
        elif (state == 2):
            moveForward2()
        elif (state == 3):
            stopState()
        else:
            pass

def moveForward():
    getData()
    motorUpdates()
    sendMotorCommands()
    global lines_hit
    if (lines_hit>=2):
        lines_hit = 0
        global state
        state = 2
        print("turning right")
        turnRight()

def turnRight(): 
    global leftMotor, rightMotor
    leftMotor = -100
    rightMotor = 100
    sendMotorCommands()
    sleep(0.75)
    ser.flush()

def turnLeft():
    global leftMotor, rightMotor
    leftMotor = 100
    rightMotor = -100
    sendMotorCommands()
    sleep(0.75)
    ser.flush()

def moveForward2():
    getData()
    motorUpdates()
    sendMotorCommands()
    if (lines_hit>=1):
        global state 
        state = 3
        print("turning left")
        turnLeft()

def stopState():
    global leftMotor, rightMotor
    global leftMotor, rightMotor
    leftMotor = 0
    rightMotor = 0
    sendMotorCommands()
    print("stopping")
    exit()
    pass


def sendMotorCommands():
    global leftMotor, rightMotor
    sendString('/dev/ttyACM0',115200,'<'+str(leftMotor)+','+str(rightMotor)+'>',0.0001)

def getData():
    if ser.in_waiting > 0:  #we waisendString('/dev/ttyACM0',115200,'<'+str(leftMotor)+','+str(rightMotor)+'>',0.0001)t until the arduino has sent something to us before we try to read anything from the serial port.     
        line = ser.readline().decode('utf-8')
        line=line.split(',')
        #this splits the incoming string up by commas
        try:
            global incomingData
            for i in range(len(line)):
                incomingData[i]=float(line[i])


        except:
            print("packet dropped") #this is designed to catch when python shoves bits on top of each other. 
            
def motorUpdates():          
    #Following is my control law, we're keeping it basic for now, writing good control law is your job
    #ok so high numbers(highest 7000) on the line follwing mean I am too far to the LEFT,
    #low numbers mean I am too far on the RIGHT, 3500 means I am at the middle
    #below is a basic control law you can send to your motors, with an exeption if z is a value greater than 7000, meaning the arduino code sees that the line sensor is on a cross. Feel free to take insperation from this,
    #but you will need to impliment a state machine similar to what you made in lab 2 (including a way of counting time without blocking) 
    global incomingData
    global lines_hit
    global leftMotor, rightMotor
    global intersectionTimer
    global lineHit

    if (not(incomingData[0]>999 and incomingData[1]>999 and incomingData[6]>999 and incomingData[7]>999)):
        leftMotor=50+.02*incomingData[10] #now that we are SURE that z isnt the string cross, we cast z to an int and recalculate leftMotor and rightMotor, 
        rightMotor=200-.02*incomingData[10]
        lineHit = False
    elif ((time.time()-intersectionTimer>2) and (not lineHit)):
        print('at intersection')
        lines_hit = lines_hit+1
        intersectionTimer=time.time()
        lineHit = True
        #do something here like incrimenting a value you call 'lines_hit' to one higher, and writing code to make sure that some time (1 second should do it) 
        # passes between being able to incriment lines_hit so that it wont be incrimented a bunch of times when you hit your first cross. IE give your robot time to leave a cross
        #before allowing lines_hit to be incrimented again.


if __name__ == '__main__':
    setup()
    main()