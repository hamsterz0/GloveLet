import glm
from glm.gtc.quaternion import *
from glm.gtc import matrix_transform
from glm.gtc import matrix_access
import time
import numpy

mat4x = glm.mat4(1,2,0,1,
	 0, 1, 1, 2,
	 2, 0, 1, 0,
	 8, 5, -6, 1)

mat4y = glm.mat4(0,34,5,3,
	     5,4,2,7,
	     9,2,3,5,
	     0,5,1,1)

num4x = numpy.matrix((1,2,0,1,
	 0, 1, 1, 2,
	 2, 0, 1, 0,
	 8, 5, -6, 1)).reshape((4,4))

num4y  = numpy.matrix((0,34,5,3,
	     5,4,2,7,
	     9,2,3,5,
	     0,5,1,1)).reshape((4,4))

a = glm.mat4(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
v = glm.vec3(0,1,0)

def add(a,b):
    a.__add__(b)

def radd(a,b):
    a.__radd__(b)

def sub(a,b):
    a.__sub__(b)
    
def rsub(a,b):
    a.__rsub__(b)

def mul(a,b):
    a.__mul__(b)

def rmul(a,b):
    a.__rmul__(b)

def div(a,b):
    a.__div__(b)
    a.__truediv__(b)

def rdiv(a,b):
    a.__rdiv__(b)
    a.__rtruediv__(b)

def check(func):
    before = time.time()
    for i in range(10000):
        func(mat4x, mat4y)
    after = time.time()
    print(func, "took about", after-before,"seconds, so each operation took about", (after-before)/10000, "seconds")

def checks(func, s):
    before = time.time()
    for i in range(10000):
        func(*s)
    after = time.time()
    print(func, "took about", after-before,"seconds, so each operation took about", (after-before)/10000, "seconds")

vec4 = glm.vec4(90,4.,0,105)
def check_vec4_creation():
    checks(glm.vec4,(90,4.,0,105))
    checks(numpy.array, ((90,4.,0,105),))

check_vec4_creation()
