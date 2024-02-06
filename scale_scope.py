#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 10:09:08 2018

@author: research
"""


# This cell will import packages that we will need to run the scopes 
# and collect and analyze data.

# This package will allow you to build arrays of data points 
import numpy as np 

# This is sometimes necessary to pause the code to allow a command to 
# complete on one of the instruments.
import time 


def vscale_scope(scope, chn, tb):
	# This function will set the vertical scale on the scope.
	# It will work off of the maximum voltage measurement for the 
	# current signal. Starting from the highest precision setting, it 
	# will scale up in voltage until the signal just fits on the screen.
	
	#print(" Going vertical now") # temp marker
	
	# The DS1074 has 13 different vertical scale settings available
	# The lowest (most precise) scale is dV = 10mV/div.
	# The highest (least precises) scale is dV = 10 V/div.
	# Each of these is set of a x1 probe and should be adjusted
	# otherwise.
	
	# Set an array with the 13 possible scales available.
	vscale = np.zeros(13)
	for i in range(0,4):
	    vscale[i*3+1]=5*np.power(10.0,-i)
	    vscale[i*3+2]=2*np.power(10.0,-i)
	    vscale[i*3+3]=1*np.power(10.0,-i)
	vscale[0]=10.
	#print(vscale)
	
	# Add the channel designation into each of the root commands 
	cmd_qscl = ":"+chn+":SCAL? " # query the scale on chn
	cmd_setscl = ":"+chn+":SCAL " # with a scale appended sets scale
	cmd_mvpp = ":MEAS:ITEM VPP," + chn # set up measurement of vpp on chn
	cmd_qvpp = ":MEAS:ITEM? VPP," + chn # query vpp on chn

	
	time.sleep(14*tb+1) # make sure to collect one set of data
	
	# read in the current vpp level
	scope.write(cmd_mvpp)

	vpp = float(scope.query(cmd_qvpp))
	
	vscale_cur = float(scope.query(cmd_qscl)) # ask for the current scale
	#print(vscale_cur)
	jj=0
	while not((0.9*vscale[jj]<vscale_cur) and (vscale_cur<1.1*vscale[jj])):
		#print(jj, vscale_cur, vscale[jj])
		jj+=1
	
	#If the scale is apporpriate return with no change.
	if (vpp<8*vscale_cur) and (4*vscale_cur < vpp):
		return
	
	# This will run if the scale is too large
	while vpp<4*vscale[jj]:
		jj+=1
		scope.write(cmd_setscl+str(vscale[jj]))
		time.sleep(14*tb+1)
		vpp = float(scope.query(cmd_qvpp))
		#scope.write(cmd_qvpp)
		#vpp = float(scope.read())
		
	
	# This will run is the scale is too small
	while vpp>8*vscale[jj]:
		jj-=1
		#print(jj)
		scope.write(cmd_setscl+str(vscale[jj]))
		time.sleep(14*tb+1)
		vpp = float(scope.query(cmd_qvpp))
		#scope.write(cmd_qvpp)
		#vpp = float(scope.read())	



def hscale_scope(scope, f):
	# Rescale the horizontal axis to better display the time base
	tb = np.zeros(31)
	for i in range(0,10):
	    tb[i*3]=5*np.power(10.0,1-i)
	    tb[i*3+1]=2*np.power(10.0,1-i)
	    tb[i*3+2]=1*np.power(10.0,1-i)
	tb[30]=5.*np.power(10.,-9)
	
	j = 1
	while 12*tb[j]*f > 3:
	    j += 1
	#print("%2.1f" %(12*tb[j]*f))
	cmd = ":TIM:MAIN:SCAL " + str(tb[j])
	#print(cmd)
	scope.write(cmd)
	
