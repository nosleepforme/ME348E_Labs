#!/usr/bin/env python3
import serial
import time
import numpy as np
import RPi.GPIO as GPIO
from gpiozero import RotaryEncoder
import csv

#assign parameter values
ppr = 48 #pulse per rev for encoder 
tsample = 0.02 # sampling period for encoder reading
tdisp = 0.1 # freqency to show encoder reading on terminal
tstop = 300

# Creating PID controller object
kp = 0.6
ki = 0.5
kd = 0.01

from simple_pid import PID
pid = PID(kp, ki, kd, setpoint=150)



# create encoder object on GPIO pins 17 and 18
encoder = RotaryEncoder(17, 18, max_steps=0)

# Define motor pins forward pin (in1) 22, backward (in2) 23, PWM (en) 24
in1 = 22
in2 = 23
en = 24


# initialize values
velCurr = 0
posCurr = 0
posLast = 0
tprev = 0
tcurr = 0
tstart = time.perf_counter()
omega = 0 #radians/sec

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.HIGH)
p=GPIO.PWM(en,500)
p.start(30)


print('running code for',tstop, 'seconds...')
print('turn encoder')
opt_omega = []
while tcurr <= tstop:
	time.sleep(tsample)
	tcurr = time.perf_counter()-tstart
	posCurr = encoder.steps
	velCurr = ((posCurr-posLast)/(tcurr-tprev))/ppr # in rev/sec
	omega = 2*3.14*velCurr
	control = pid(omega)
	if(np.floor(tcurr/tdisp)-np.floor(tprev/tdisp))==1:
		print(omega)
	if control < 0:
		GPIO.output(in1,GPIO.HIGH)
		GPIO.output(in2,GPIO.LOW)
		control = -control
	else:
		GPIO.output(in1,GPIO.LOW)
		GPIO.output(in2,GPIO.HIGH)
	if control >100:
		control = 100
	p.ChangeDutyCycle(control)
	
	
	tprev = tcurr
	posLast = posCurr
#	opt_omega += [omega]
print('Done.')
# with open('/home/group3/Lab/Lab5/data.csv', 'w') as f:
# 	writer = csv.writer(f)
# 	for stuff in opt_omega:
# 		writer.writerow([stuff])

GPIO.cleanup()
encoder.close()





