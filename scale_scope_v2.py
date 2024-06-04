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


def vscale_scope(scope, chn, probe, tb):
	# This function will set the vertical scale on the scope.
	# It will work off of the maximum voltage measurement for the 
	# current signal. Starting from the highest precision setting, it 
	# will scale up in voltage until the signal just fits on the screen.
	
	#print(" Going vertical now") # temp marker
	
	# The DS1074 has 13 different vertical scale settings available
	# With the probe set as a x1 probe, the lowest (most precise) 
	# scale is dV = 1.0mV/div. The highest (least precises) scale 
	# is dV = 10 V/div.
	# These are set for a x1 probe and should be adjusted
	# acordingly. The probe setting can be used to adjust the 
	# size of the scale readings.	
	# Set an array with the 13 possible scales available.
	scope_scale = np.array([0.001, 0.002, 0.005, 0.01, 0.02, 0.05, \
							0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0])
	vscale = probe*scope_scale
			
	
	# Build commands necessary to query the channel scale setting, 
	# the vpp for the channel, and to set the scale setting. These
	# lines add the specific channel to the generic commands. 
	cmd_qscl = ":"+chn+":SCAL? " # query the scale on chn
	cmd_setscl = ":"+chn+":SCAL " # with a scale appended sets scale
	cmd_qvpp = ":MEAS:ITEM? VPP," + chn # query vpp on chn

	time.sleep(14*tb) # make sure to collect one screen of data
	
	# read in the current vpp level
	vpp = float(scope.query(cmd_qvpp))

	# read in the current vertical scale setting
	vscale_cur = float(scope.query(cmd_qscl))
	
	# determine where this scale fits in the possible values
	jj = np.where(vscale==vscale_cur)[0][0]
	
	# Adjust the scale up if needed. If the vpp covers more than 95% 
	# of the screen (0.95*8*vscale_cur), increase the scale by one 
	# click up to the max scale possible, vscale[13].
	if vpp<0.95*8*vscale_cur and vpp>0.5*8*vscale_cur:
		# This is the optimal range for vertical measurements
		# you are done here.
		#print('optimal range found')
		return

	while vpp>0.95*8*vscale_cur:
		if jj<13:
			jj += 1
		else:
			print("The signal is too large for the current probe \
			settings, consider using a larger probe setting.")
			return	
		scope.write(cmd_setscl+str(vscale[jj]))
		time.sleep(12*tb) # make sure to collect one screen of data
		vscale_cur = float(scope.query(cmd_qscl))
		time.sleep(14*tb+1)
		vpp = float(scope.query(cmd_qvpp))
	
		
	# This will run if the scale is too large. The idea is to set the 
	# scale so that the signal takes up more than half the screen
	# if possible.
	# read in the current vpp level
	vpp = float(scope.query(cmd_qvpp))

	# read in the current vertical scale setting
	vscale_cur = float(scope.query(cmd_qscl))
	while vpp<0.5*8*vscale_cur:
		if jj>0:
			jj-=1
		else:
			# You scale cannot be lowered any more. The signal is too
			# small and measurements may be unreliable.
			return
		scope.write(cmd_setscl+str(vscale[jj]))
		vscale_cur = float(scope.query(cmd_qscl))
		time.sleep(12*tb)
		vpp = float(scope.query(cmd_qvpp))
	vmax = float(scope.query(":MEAS:ITEM? VMAX,"+chn))
	vmin = float(scope.query(":MEAS:ITEM? VMIN,"+chn))
	if vmax>vscale_cur*4 or vmin<-4*vscale_cur:
		jj+=1
		scope.write(cmd_setscl+str(vscale[jj]))
		
	return
		


def hscale_scope(scope, f):
	# Rescale the horizontal axis to better display the time base
	# The scales are set for a Rigol DS1074z scope. Actual values
	# may be different for different scopes.

	tb = np.array([5.0e-9, 1.0e-8, 2.0e-8, 5.0e-8, \
						   1.0e-7, 2.0e-7, 5.0e-7, \
						   1.0e-6, 2.0e-6, 5.0e-6, \
						   1.0e-5, 2.0e-5, 5.0e-5, \
						   1.0e-4, 2.0e-4, 5.0e-4, \
						   1.0e-3, 2.0e-3, 5.0e-3, \
						   1.0e-2, 2.0e-2, 5.0e-2, \
						   1.0e-1, 2.0e-1, 5.0e-1, \
						   1.0e0,  2.0e0,  5.0e0, \
						   1.0e1,  2.0e1,  5.0e1])
	
	tb_cur = float(scope.query(":TIM:SCAL?"))
	
	j = np.where(tb==tb_cur)[0][0]

	# Set the scope timebase to show between 2 and 4 cycles of the
	# signal being measured.
	
	i=0
	while 12*tb[j]*f >= 4 or 12*tb[j]*f <= 2:
		if 12*tb[j]*f > 4.0:
			j -= 1
			i += 1
		if 12*tb[j]*f < 2.0:
			j += 1
			i += 1
		if i>31:
			return
			
	cmd = ":TIM:MAIN:SCAL " + str(tb[j])
	
	scope.write(cmd)
	
