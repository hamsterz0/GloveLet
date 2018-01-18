from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import serial
import numpy as np

arduino = serial.Serial('/dev/ttyACM0', 38400, timeout=1)

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def resize(width, height):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def read_data():
    line = arduino.readline().decode("utf-8")
    data = line.split(' ')
    accel, gyro = [], []
    if len(data) == 6:
        accel = [float(data[0]), float(data[1]), float(data[2])]
        gyro = [float(data[3])-362.00, float(data[4])-318.00, float(data[5])+570.00]
        print('{} {} {} {} {} {}'.format(*accel, *gyro))
    return gyro

# @arnav: Joseph, you will have to update this part for getting a better
#         OpenGL GUI
def draw(gx, gy, gz):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	
    glLoadIdentity()

    # Test the rotational transform here. 
    glTranslatef(0, 0.0, -7.0)
    glRotatef(gz, 0.0, 1.0, 0.0)
    glRotatef(gy, 1.0, 0.0, 0.0)
    glRotatef(-1*gx, 0.0, 0.0, 1.0)

    glBegin(GL_QUADS)	
    glColor3f(0.0,1.0,0.0)
    glVertex3f( 1.0, 0.2,-1.0)
    glVertex3f(-1.0, 0.2,-1.0)		
    glVertex3f(-1.0, 0.2, 1.0)		
    glVertex3f( 1.0, 0.2, 1.0)		

    glColor3f(1.0,0.5,0.0)	
    glVertex3f( 1.0,-0.2, 1.0)
    glVertex3f(-1.0,-0.2, 1.0)		
    glVertex3f(-1.0,-0.2,-1.0)		
    glVertex3f( 1.0,-0.2,-1.0)		

    glColor3f(1.0,0.0,0.0)		
    glVertex3f( 1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)		
    glVertex3f(-1.0,-0.2, 1.0)		
    glVertex3f( 1.0,-0.2, 1.0)		

    glColor3f(1.0,1.0,0.0)	
    glVertex3f( 1.0,-0.2,-1.0)
    glVertex3f(-1.0,-0.2,-1.0)
    glVertex3f(-1.0, 0.2,-1.0)		
    glVertex3f( 1.0, 0.2,-1.0)		

    glColor3f(0.0,0.0,1.0)	
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2,-1.0)		
    glVertex3f(-1.0,-0.2,-1.0)		
    glVertex3f(-1.0,-0.2, 1.0)		

    glColor3f(1.0,0.0,1.0)	
    glVertex3f( 1.0, 0.2,-1.0)
    glVertex3f( 1.0, 0.2, 1.0)
    glVertex3f( 1.0,-0.2, 1.0)		
    glVertex3f( 1.0,-0.2,-1.0)		
    glEnd()	 

if __name__ == '__main__':
    width = 640
    height = 480
    ax, ay, az = 0.0, 0.0, 0.0
    gx, gy, gz = 0.0, 0.0, 0.0
    pygame.init()
    screen = pygame.display.set_mode((width, height), OPENGL|DOUBLEBUF)
    resize(width, height)
    init()
    ticks = pygame.time.get_ticks()
    while True:
        gyro = read_data()
        if len(gyro) != 3:
            continue
        [gx, gy, gz] = gyro #unpacking
        draw(gx, gy, gz)
        pygame.display.flip()

