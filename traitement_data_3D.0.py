import socket
import numpy as np
from struct import *
import pyvista as pv
import math
import matplotlib.pyplot as plt

#paramètre de prise de mesure
tours = 4   #nombre de tour à spécifier
angle = 310 #angle de prise de vue du lidar paramètrer via htpp://192.168.1.201

#défini l'élévation en fonction de l'ordre des lasers
elevation = np.array([-15,1,-13,3,-11,5,-9,7,-7,9,-5,11,-3,13,-1,15])
elevation = elevation.astype(float)
elevation = np.radians(elevation)
#écoute toute les info entrante sur le port spécifié
UDP_IP = "0.0.0.0"
UDP_PORT = 2368
#ouverture du port
sock = socket.socket(socket.AF_INET, 
                     socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))


# initialisation de data
data=np.array([np.zeros(65)])

#boucle d'aquisition des data packets
for times in range(math.ceil(angle/4.8*(tours+2))):
    dataBytes, addr = sock.recvfrom(1206)
       
    # convertit les bytes hexadécimal en décimal
    for i in np.arange(12):
         bloc=dataBytes[i*100:(i*100)+100] #défini le datapacket à enregistrer
         data= np.concatenate((np.array([np.asarray(unpack('<HHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHBHB',bloc[2:]))]),data), axis = 0) # enregistre le datapacket et transforme les valeurs en hexa 
data = data[:-1] 
with open('data.npy', 'rb') as f:

    w = np.load(f)

#calcul de l'azimuth des données
azimuth = np.divide(data[:,0],100)

# découpage des balayage de mesure sucessive
pos=np.where((azimuth[1:]-azimuth[0:-1])>1)
step = np.min([pos[0][1:]-pos[0][0:-1]])

#initialisation des array
dataFinal = np.zeros((1,step,32))
azimuthFinal= np.zeros((1,step))

#création d'un array 3D pour les distance et la réflectivité en fonction de l'azimuth et de l'élévation + array 3dpour les azimuth
for i in range(1,len(pos[0])-1):
    dist = data[step*i:step*(i+1),1:]
    dist1 = dist[:,:32]
    dist2 = dist[:, 32:64]
    azi = data[step*i:step*(i+1),0]
    dataFinal = np.concatenate((np.array([dist2]),np.array([dist1]),dataFinal))
    azimuthFinal = np.concatenate((np.array([azi]),azimuthFinal))

dataFinal = dataFinal[0:-1]
azimuthFinal = np.radians(azimuthFinal[0:-1]/100)
#colone : une distance+une réflectivité par élévation, ligne: 32 nombres par azimuth


#initailisation de coords
coords= np.zeros((1,3))
# calcul des coordonées
for a in range(len(dataFinal[0])):
    x = np.multiply.reduce((dataFinal[0][a][0::2]*2/1000,np.cos(elevation),np.sin(azimuthFinal[0][a])))
    y = np.multiply.reduce(((dataFinal[0][a][0::2]*2/1000), np.cos(elevation),np.cos(azimuthFinal[0][a])))
    z = np.multiply(dataFinal[0][a][0::2]*2/1000, np.sin(elevation))
    
    # mise en ordre des coordonées : x,y,z ,x,y,z,...
    for f in range(len(x)):
        coords = np.concatenate((np.array([[x[f],y[f],z[f]]]),coords))
#affichage en 3D
pv.plot(coords,scalars= coords[:,2],render_points_as_spheres= True,point_size= 4)

