import socket
import numpy as np
from struct import *
import pyvista as pv
import math
import matplotlib.pyplot as plt

#measurement parameter
tours = 4   #number of revolutions to be specified
angle = 310 #lidar angle of view set via htpp://192.168.1.201

#defines elevation as a function of laser order
elevation = np.array([-15,1,-13,3,-11,5,-9,7,-7,9,-5,11,-3,13,-1,15])
elevation = elevation.astype(float)
elevation = np.radians(elevation)
#listens to all incoming info on the specified port
UDP_IP = "0.0.0.0"
UDP_PORT = 2368
#port opening
sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


# data initialization
data=np.array([np.zeros(65)])

#data packet acquisition loop
for times in range(math.ceil(angle/4.8*(tours+2))):
    dataBytes, addr = sock.recvfrom(1206)
       
    # converts hexadecimal bytes to decimal
    for i in np.arange(12):
         bloc=dataBytes[i*100:(i*100)+100] #defines the datapacket to be saved
         data= np.concatenate((np.array([np.asarray(unpack('<HHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHB',bloc[2:]))]),data), axis = 0) # saves the datapacket and transforms the values into hexa 
data = data[:-1] 
with open('data.npy', 'rb') as f:

    w = np.load(f)

# calculation of data azimuth
azimuth = np.divide(data[:,0],100)

# sucessive sweep cutting
pos=np.where((azimuth[1:]-azimuth[0:-1])>1)
step = np.min([pos[0][1:]-pos[0][0:-1]])

#initializing arrays
dataFinal = np.zeros((1,step,32))
azimuthFinal= np.zeros((1,step))

#creation of a 3D array for distance and reflectivity as a function of azimuth and elevation + 2d array for azimuths
for i in range(1,len(pos[0])-1):
    dist = data[step*i:step*(i+1),1:]
    dist1 = dist[:,:32]
    dist2 = dist[:, 32:64]
    azi = data[step*i:step*(i+1),0]
    dataFinal = np.concatenate((np.array([dist2]),np.array([dist1]),dataFinal))
    azimuthFinal = np.concatenate((np.array([azi]),azimuthFinal))

dataFinal = dataFinal[0:-1]
azimuthFinal = np.radians(azimuthFinal[0:-1]/100)
#column: one distance+one reflectivity per elevation, line: 16 numbers per azimuth


#initailization of coords
coords= np.zeros((1,3))
# coordinate calculation
for a in range(len(dataFinal[0])):
    x = np.multiply.reduce((dataFinal[0][a][0::2]*2/1000,np.cos(elevation),np.sin(azimuthFinal[0][a])))
    y = np.multiply.reduce(((dataFinal[0][a][0::2]*2/1000), np.cos(elevation),np.cos(azimuthFinal[0][a])))
    z = np.multiply(dataFinal[0][a][0::2]*2/1000, np.sin(elevation))
    
    # coordinate ordering: x,y,z ,x,y,z,...
    for f in range(len(x)):
        coords = np.concatenate((np.array([[x[f],y[f],z[f]]]),coords))
#3D display
pv.plot(coords,scalars= coords[:,2],render_points_as_spheres= True,point_size= 4)

