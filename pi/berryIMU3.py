# This code runs on the IMU,

#!/usr/bin/python
#
#    This program  reads the angles from the acceleromteer, gyroscope
#    and mangnetometer on a BerryIMU connected to a Raspberry Pi.
#
#    This program includes two filters (low pass and median) to improve the
#    values returned from BerryIMU by reducing noise.
#
#    The BerryIMUv1, BerryIMUv2 and BerryIMUv3 are supported
#
#    This script is python 2.7 and 3 compatible
#
#    Feel free to do whatever you like with this code.
#    Distributed as-is; no warranty is given.
#
#    http://ozzmaker.com/



import sys
import time
import math
import IMU
import datetime
import os
from ably import AblyRest
import paho.mqtt.client as mqtt
import asyncio
import requests
import json
import subprocess

MQTT_HOST = 'mqtt.ably.io'
MQTT_PORT = 1883  # default MQTT port
MQTT_TOPIC = 'controller:1'

RAD_TO_DEG = 57.29578
M_PI = 3.14159265358979323846
G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
AA =  0.40              # Complementary filter constant
MAG_LPF_FACTOR = 0.4    # Low pass filter constant magnetometer
ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer
ACC_MEDIANTABLESIZE = 9  # Median filter table size for accelerometer. Higher = smoother but a longer delay
MAG_MEDIANTABLESIZE = 9 # Median filter table size for magnetometer. Higher = smoother but a longer delay
DELTA_TIME = 0.1

################# Compass Calibration values ############
# Use calibrateBerryIMU.py to get calibration values
# Calibrating the compass isnt mandatory, however a calibrated
# compass will result in a more accurate heading value.

# magXmin  311  magYmin  -928  magZmin  -4927  ## magXmax  339  magYmax  -899  magZmax -4864  
magXmin = -730
magYmin = -1532
magZmin = -4407
magXmax = 1313
magYmax = -881
magZmax = -3447
############### END Calibration offsets #################


#Kalman filter variables
Q_angle = 0.02
Q_gyro = 0.0015
R_angle = 0.005
y_bias = 0.0
x_bias = 0.0
XP_00 = 0.0
XP_01 = 0.0
XP_10 = 0.0
XP_11 = 0.0
YP_00 = 0.0
YP_01 = 0.0
YP_10 = 0.0
YP_11 = 0.0
KFangleX = 0.0
KFangleY = 0.0
prev_kalmanX = 0
prev_kalmanY = 0
velocity_x = 0.0
velocity_y = 0.0
velocity_z = 0.0

# ADDED CODE

# Constants
ROLLING_AVERAGE_SIZE = 10  # Number of samples to consider for rolling average

# Initialize buffers for rolling average
acc_buffer_x = [0] * ROLLING_AVERAGE_SIZE
acc_buffer_y = [0] * ROLLING_AVERAGE_SIZE
acc_buffer_z = [0] * ROLLING_AVERAGE_SIZE

def update_buffer(buffer, value):
	buffer.pop(0)  # Remove the oldest element
	buffer.append(value)  # Add the newest element
	return buffer

def calculate_average(buffer):
	return sum(buffer) / len(buffer)

def kalmanFilterY ( accAngle, gyroRate, DT):
	y=0.0
	S=0.0
	
	global KFangleY
	global Q_angle
	global Q_gyro
	global y_bias
	global YP_00
	global YP_01
	global YP_10
	global YP_11
	
	KFangleY = KFangleY + DT * (gyroRate - y_bias)
	
	YP_00 = YP_00 + ( - DT * (YP_10 + YP_01) + Q_angle * DT )
	YP_01 = YP_01 + ( - DT * YP_11 )
	YP_10 = YP_10 + ( - DT * YP_11 )
	YP_11 = YP_11 + ( + Q_gyro * DT )
	
	y = accAngle - KFangleY
	S = YP_00 + R_angle
	K_0 = YP_00 / S
	K_1 = YP_10 / S
	
	KFangleY = KFangleY + ( K_0 * y )
	y_bias = y_bias + ( K_1 * y )
	
	YP_00 = YP_00 - ( K_0 * YP_00 )
	YP_01 = YP_01 - ( K_0 * YP_01 )
	YP_10 = YP_10 - ( K_1 * YP_00 )
	YP_11 = YP_11 - ( K_1 * YP_01 )
	
	return KFangleY

def kalmanFilterX ( accAngle, gyroRate, DT):
	x=0.0
	S=0.0
	
	global KFangleX
	global Q_angle
	global Q_gyro
	global x_bias
	global XP_00
	global XP_01
	global XP_10
	global XP_11
	
	
	KFangleX = KFangleX + DT * (gyroRate - x_bias)
	
	XP_00 = XP_00 + ( - DT * (XP_10 + XP_01) + Q_angle * DT )
	XP_01 = XP_01 + ( - DT * XP_11 )
	XP_10 = XP_10 + ( - DT * XP_11 )
	XP_11 = XP_11 + ( + Q_gyro * DT )
	
	x = accAngle - KFangleX
	S = XP_00 + R_angle
	K_0 = XP_00 / S
	K_1 = XP_10 / S
	
	KFangleX = KFangleX + ( K_0 * x )
	x_bias = x_bias + ( K_1 * x )
	
	XP_00 = XP_00 - ( K_0 * XP_00 )
	XP_01 = XP_01 - ( K_0 * XP_01 )
	XP_10 = XP_10 - ( K_1 * XP_00 )
	XP_11 = XP_11 - ( K_1 * XP_01 )
	
	return KFangleX


gyroXangle = 0.0
gyroYangle = 0.0
gyroZangle = 0.0
CFangleX = 0.0
CFangleY = 0.0
CFangleXFiltered = 0.0
CFangleYFiltered = 0.0
kalmanX = 0.0
kalmanY = 0.0
oldXMagRawValue = 0
oldYMagRawValue = 0
oldZMagRawValue = 0
oldXAccRawValue = 0
oldYAccRawValue = 0
oldZAccRawValue = 0

a = datetime.datetime.now()


#Setup the tables for the mdeian filter. Fill them all with '1' so we dont get devide by zero error
acc_medianTable1X = [1] * ACC_MEDIANTABLESIZE
acc_medianTable1Y = [1] * ACC_MEDIANTABLESIZE
acc_medianTable1Z = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2X = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2Y = [1] * ACC_MEDIANTABLESIZE
acc_medianTable2Z = [1] * ACC_MEDIANTABLESIZE
mag_medianTable1X = [1] * MAG_MEDIANTABLESIZE
mag_medianTable1Y = [1] * MAG_MEDIANTABLESIZE
mag_medianTable1Z = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2X = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2Y = [1] * MAG_MEDIANTABLESIZE
mag_medianTable2Z = [1] * MAG_MEDIANTABLESIZE

IMU.detectIMU()     #Detect if BerryIMU is connected.
if(IMU.BerryIMUversion == 99):
	print(" No BerryIMU found... exiting ")
	sys.exit()
IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass

ORIENTATION_CHANGE_THRESHOLD = 5.0  # Degrees

#async def ablyconnect():
#    ably = AblyRealtime("zsW-PQ.nSlItw:zqlmeBRBlN7nYanF6LzG4ZlsgSn_3O9I-J0LVMgr7m0")
#    await ably.connection.once_async('connected')
#    print('Connected to Ably')

#asyncio.run(ablyconnect())

#client = AblyRest("zsW-PQ.nSlItw:zqlmeBRBlN7nYanF6LzG4ZlsgSn_3O9I-J0LVMgr7m0")

async def run_command_async(command):
    await asyncio.create_subprocess_shell(command)

def main():

		MQTT_HOST = 'mqtt.ably.io'
		MQTT_PORT = 1883  # default MQTT port
		MQTT_TOPIC = 'controller:1'

		RAD_TO_DEG = 57.29578
		M_PI = 3.14159265358979323846
		G_GAIN = 0.070          # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
		AA =  0.40              # Complementary filter constant
		MAG_LPF_FACTOR = 0.4    # Low pass filter constant magnetometer
		ACC_LPF_FACTOR = 0.4    # Low pass filter constant for accelerometer
		ACC_MEDIANTABLESIZE = 9  # Median filter table size for accelerometer. Higher = smoother but a longer delay
		MAG_MEDIANTABLESIZE = 9 # Median filter table size for magnetometer. Higher = smoother but a longer delay
		DELTA_TIME = 0.1

		a = datetime.datetime.now()
		gyroXangle = 0.0
		gyroYangle = 0.0
		gyroZangle = 0.0
		CFangleX = 0.0
		CFangleY = 0.0
		CFangleXFiltered = 0.0
		CFangleYFiltered = 0.0
		kalmanX = 0.0
		kalmanY = 0.0
		oldXMagRawValue = 0
		oldYMagRawValue = 0
		oldZMagRawValue = 0
		oldXAccRawValue = 0
		oldYAccRawValue = 0
		oldZAccRawValue = 0
		
		magXmin = -730
		magYmin = -1532
		magZmin = -4407
		magXmax = 1313
		magYmax = -881
		magZmax = -3447
		
		#Kalman filter variables
		Q_angle = 0.02
		Q_gyro = 0.0015
		R_angle = 0.005
		y_bias = 0.0
		x_bias = 0.0
		XP_00 = 0.0
		XP_01 = 0.0
		XP_10 = 0.0
		XP_11 = 0.0
		YP_00 = 0.0
		YP_01 = 0.0
		YP_10 = 0.0
		YP_11 = 0.0
		KFangleX = 0.0
		KFangleY = 0.0
		prev_kalmanX = 0
		prev_kalmanY = 0
		velocity_x = 0.0
		velocity_y = 0.0
		velocity_z = 0.0
		
		#Setup the tables for the mdeian filter. Fill them all with '1' so we dont get devide by zero error
		acc_medianTable1X = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable1Y = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable1Z = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable2X = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable2Y = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable2Z = [1] * ACC_MEDIANTABLESIZE
		mag_medianTable1X = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable1Y = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable1Z = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable2X = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable2Y = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable2Z = [1] * MAG_MEDIANTABLESIZE
		
		ROLLING_AVERAGE_SIZE = 10  # Number of samples to consider for rolling average

		# Initialize buffers for rolling average
		acc_buffer_x = [0] * ROLLING_AVERAGE_SIZE
		acc_buffer_y = [0] * ROLLING_AVERAGE_SIZE
		acc_buffer_z = [0] * ROLLING_AVERAGE_SIZE
		
		IMU.detectIMU()     #Detect if BerryIMU is connected.
		if(IMU.BerryIMUversion == 99):
			print(" No BerryIMU found... exiting ")
			sys.exit()
		IMU.initIMU()       #Initialise the accelerometer, gyroscope and compass

		ORIENTATION_CHANGE_THRESHOLD = 5.0  # Degrees

		username = "zsW-PQ.nSlItw"
		password = "zqlmeBRBlN7nYanF6LzG4ZlsgSn_3O9I-J0LVMgr7m0"

		mqttc = mqtt.Client(client_id="Test", clean_session=True, userdata=None)
		mqttc.username_pw_set(username, password)
		mqttc.connect(MQTT_HOST, port=MQTT_PORT, keepalive=15)
	
		while True:
			
			prev_time = datetime.datetime.now()
			
			#Read the accelerometer,gyroscope and magnetometer values
			ACCx = IMU.readACCx()
			ACCy = IMU.readACCy()
			ACCz = IMU.readACCz()
			GYRx = IMU.readGYRx()
			GYRy = IMU.readGYRy()
			GYRz = IMU.readGYRz()
			MAGx = IMU.readMAGx()
			MAGy = IMU.readMAGy()
			MAGz = IMU.readMAGz()
			
			
			#Apply compass calibration
			MAGx -= (magXmin + magXmax) /2
			MAGy -= (magYmin + magYmax) /2
			MAGz -= (magZmin + magZmax) /2
			
			
			##Calculate loop Period(LP). How long between Gyro Reads
			b = datetime.datetime.now() - a
			a = datetime.datetime.now()
			LP = b.microseconds/(1000000*1.0)
			outputString = "Loop Time %5.2f " % ( LP )
			
			
			###############################################
			#### Apply low pass filter ####
			###############################################
			MAGx =  MAGx  * MAG_LPF_FACTOR + oldXMagRawValue*(1 - MAG_LPF_FACTOR);
			MAGy =  MAGy  * MAG_LPF_FACTOR + oldYMagRawValue*(1 - MAG_LPF_FACTOR);
			MAGz =  MAGz  * MAG_LPF_FACTOR + oldZMagRawValue*(1 - MAG_LPF_FACTOR);
			ACCx =  ACCx  * ACC_LPF_FACTOR + oldXAccRawValue*(1 - ACC_LPF_FACTOR);
			ACCy =  ACCy  * ACC_LPF_FACTOR + oldYAccRawValue*(1 - ACC_LPF_FACTOR);
			ACCz =  ACCz  * ACC_LPF_FACTOR + oldZAccRawValue*(1 - ACC_LPF_FACTOR);
			
			oldXMagRawValue = MAGx
			oldYMagRawValue = MAGy
			oldZMagRawValue = MAGz
			oldXAccRawValue = ACCx
			oldYAccRawValue = ACCy
			oldZAccRawValue = ACCz
			
			#########################################
			#### Median filter for accelerometer ####
			#########################################
			# cycle the table
			for x in range (ACC_MEDIANTABLESIZE-1,0,-1 ):
				acc_medianTable1X[x] = acc_medianTable1X[x-1]
				acc_medianTable1Y[x] = acc_medianTable1Y[x-1]
				acc_medianTable1Z[x] = acc_medianTable1Z[x-1]
				
				# Insert the lates values
				acc_medianTable1X[0] = ACCx
				acc_medianTable1Y[0] = ACCy
				acc_medianTable1Z[0] = ACCz
				
				# Copy the tables
				acc_medianTable2X = acc_medianTable1X[:]
				acc_medianTable2Y = acc_medianTable1Y[:]
				acc_medianTable2Z = acc_medianTable1Z[:]
				
			# Sort table 2
			acc_medianTable2X.sort()
			acc_medianTable2Y.sort()
			acc_medianTable2Z.sort()
			
			# The middle value is the value we are interested in
			ACCx = acc_medianTable2X[int(ACC_MEDIANTABLESIZE/2)];
			ACCy = acc_medianTable2Y[int(ACC_MEDIANTABLESIZE/2)];
			ACCz = acc_medianTable2Z[int(ACC_MEDIANTABLESIZE/2)];
			
			#########################################
			#### Median filter for magnetometer ####
			#########################################
			# cycle the table
			for x in range (MAG_MEDIANTABLESIZE-1,0,-1 ):
				mag_medianTable1X[x] = mag_medianTable1X[x-1]
				mag_medianTable1Y[x] = mag_medianTable1Y[x-1]
				mag_medianTable1Z[x] = mag_medianTable1Z[x-1]
				
				# Insert the latest values
				mag_medianTable1X[0] = MAGx
				mag_medianTable1Y[0] = MAGy
				mag_medianTable1Z[0] = MAGz
				
				# Copy the tables
				mag_medianTable2X = mag_medianTable1X[:]
				mag_medianTable2Y = mag_medianTable1Y[:]
				mag_medianTable2Z = mag_medianTable1Z[:]
				
			# Sort table 2
			mag_medianTable2X.sort()
			mag_medianTable2Y.sort()
			mag_medianTable2Z.sort()
			
			# The middle value is the value we are interested in
			MAGx = mag_medianTable2X[int(MAG_MEDIANTABLESIZE/2)];
			MAGy = mag_medianTable2Y[int(MAG_MEDIANTABLESIZE/2)];
			MAGz = mag_medianTable2Z[int(MAG_MEDIANTABLESIZE/2)];
			
			#Convert Gyro raw to degrees per second
			rate_gyr_x =  GYRx * G_GAIN
			rate_gyr_y =  GYRy * G_GAIN
			rate_gyr_z =  GYRz * G_GAIN
			
			#Calculate the angles from the gyro.
			gyroXangle+=rate_gyr_x*LP
			gyroYangle+=rate_gyr_y*LP
			gyroZangle+=rate_gyr_z*LP
			
			#Convert Accelerometer values to degrees
			AccXangle =  (math.atan2(ACCy,ACCz)*RAD_TO_DEG)
			AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG
			
			#Change the rotation value of the accelerometer to -/+ 180 and
			#move the Y axis '0' point to up.  This makes it easier to read.
			if AccYangle > 90:
				AccYangle -= 270.0
			else:
				AccYangle += 90.0
			
			
			#Complementary filter used to combine the accelerometer and gyro values.
			CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
			CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle
			
			#Kalman filter used to combine the accelerometer and gyro values.
			kalmanY = kalmanFilterY(AccYangle, rate_gyr_y,LP)
			kalmanX = kalmanFilterX(AccXangle, rate_gyr_x,LP)
			
			#Calculate heading
			heading = 180 * math.atan2(MAGy,MAGx)/M_PI
			
			#Only have our heading between 0 and 360
			if heading < 0:
				heading += 360
			
			####################################################################
			###################Tilt compensated heading#########################
			####################################################################
			#Normalize accelerometer raw values.
			accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
			accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
			
			#Calculate pitch and roll
			pitch = math.asin(accXnorm)
			roll = -math.asin(accYnorm/math.cos(pitch))
			
			#Calculate the new tilt compensated values
			#The compass and accelerometer are orientated differently on the the BerryIMUv1, v2 and v3.
			#This needs to be taken into consideration when performing the calculations
			
			#X compensation
			if(IMU.BerryIMUversion == 1 or IMU.BerryIMUversion == 3):            #LSM9DS0 and (LSM6DSL & LIS2MDL)
				magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)
			else:                                                                #LSM9DS1
				magXcomp = MAGx*math.cos(pitch)-MAGz*math.sin(pitch)
			
			#Y compensation
			if(IMU.BerryIMUversion == 1 or IMU.BerryIMUversion == 3):            #LSM9DS0 and (LSM6DSL & LIS2MDL)
				magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)
			else:                                                                #LSM9DS1
				magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)+MAGz*math.sin(roll)*math.cos(pitch)
			
			#Calculate tilt compensated heading
			tiltCompensatedHeading = 180 * math.atan2(magYcomp,magXcomp)/M_PI
			
			if tiltCompensatedHeading < 0:
				tiltCompensatedHeading += 360
			
			
			##################### END Tilt Compensation ########################
			
			
			if 0:                       #Change to '0' to stop showing the angles from the accelerometer
				outputString += "#  ACCX Angle %5.2f ACCY Angle %5.2f  #  " % (AccXangle, AccYangle)
			
			if 0:                       #Change to '0' to stop  showing the angles from the gyro
				outputString +="\t# GRYX Angle %5.2f  GYRY Angle %5.2f  GYRZ Angle %5.2f # " % (gyroXangle,gyroYangle,gyroZangle)
			
			if 0:                       #Change to '0' to stop  showing the angles from the complementary filter
				outputString +="\t#  CFangleX Angle %5.2f   CFangleY Angle %5.2f  #" % (CFangleX,CFangleY)
			
			if 0:                       #Change to '0' to stop  showing the heading
				outputString +="\t# HEADING %5.2f  tiltCompensatedHeading %5.2f #" % (heading,tiltCompensatedHeading)
			
			if 0:                       #Change to '0' to stop  showing the angles from the Kalman filter
				outputString +="# kalmanX %5.2f   kalmanY %5.2f #" % (kalmanX,kalmanY)
			
			#outputString +="# accX %5.2f    accY %5.2f   accZ%5.2f #" % (ACCx,ACCy,ACCz)
				
			current_time = datetime.datetime.now()
			delta_time = (current_time - prev_time).total_seconds()
			prev_time = current_time
			
			if abs(kalmanX - prev_kalmanX) > ORIENTATION_CHANGE_THRESHOLD or abs(kalmanY - prev_kalmanY) > ORIENTATION_CHANGE_THRESHOLD:
				#print("Significant orientation change detected")
				pass
				
			prev_kalmanX = kalmanX
			prev_kalmanY = kalmanY
			
			#if delta_time >= 0.05:
			'''
			strout = "Kalman X: {:.2f}, Y: {:.2f}, Heading: {:.2f}".format(kalmanX, kalmanY, tiltCompensatedHeading)
			command = 'curl -X POST https://rest.ably.io/channels/test-channel/messages -u "zsW-PQ.nSlItw:zqlmeBRBlN7nYanF6LzG4ZlsgSn_3O9I-J0LVMgr7m0" -H "Content-Type: application/json" --data \'{"name": "publish", "data": "{}"}\''.format(strout)
			print(command)
			'''
			
			formatted_string = "accX: {:.5f}, accY: {:.5f}, accZ: {:.5f}, heading: {:.5f}".format(ACCx, ACCy, ACCz, heading)
			mqttc.publish(MQTT_TOPIC, formatted_string)
		
			'''
			data_to_send = {
				"name": "publish",
				"data": strout
			}
			headers = {
				"Content-Type": "application/json",
			}
			url = "https://rest.ably.io/channels/test-channel/messages"
			response = requests.post(url, headers=headers, auth=("zsW-PQ.nSlItw", "zqlmeBRBlN7nYanF6LzG4ZlsgSn_3O9I-J0LVMgr7m0"), json=data_to_send)

			#slow program down a bit, makes the output more readable
			
			'''
			time.sleep(0.15)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	try:
		loop.run_until_complete(main())
	finally:
			loop.close()
