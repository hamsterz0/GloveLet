from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import serial

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

ax, ay, az = 0.0, 0.0, 0.0
gx, gy, gz = 0.0, 0.0, 0.0

arduino = serial.Serial('/dev/ttyACM0', 38400, timeout=1)


def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def resize():
    global SCREEN_HEIGHT
    global SCREEN_WIDTH
    if SCREEN_HEIGHT==0:
        SCREEN_HEIGHT=1
    glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*SCREEN_WIDTH/SCREEN_HEIGHT, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def read_data():
    global ax, ay, az
    global gx, gy, gz
    line = arduino.readline().decode("utf-8")
    data = line.split(' ')
    if len(data) == 6:
        ax, ay, az = float(data[0]), float(data[1]), float(data[2])
        gx, gy, gz = float(data[3]), float(data[4]), float(data[5])
    print('{} {} {} {} {} {}'.format(ax, ay, ax, gx, gy, gz))

def draw():
    global ax, ay, az
    global gx, gy, gz
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	
    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    glRotatef(az, 0.0, 1.0, 0.0)
    glRotatef(ay, 1.0, 0.0, 0.0)
    glRotatef(-1*ax, 0.0, 0.0, 1.0)

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
    global SCREEN_WIDTH
    global SCREEN_HEIGHT
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), OPENGL|DOUBLEBUF)
    resize()
    init()
    ticks = pygame.time.get_ticks()
    while True:
        read_data()
        draw()
        pygame.display.flip()

