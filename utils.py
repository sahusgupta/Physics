from typing import Union
import cmath as c
from vectors.Vector2D import Vector2D
from vectors.Vector1D import Vector1D
from vectors.Vector3D import Vector3D

def angle_between(vector1: Union[Vector2D, Vector1D, Vector3D], vector2: Union[Vector2D, Vector1D, Vector3D]):
    return c.acos(vector1.dotproduct(vector2) / (vector1.magnitude * vector2.magnitude)) * (180 / c.pi)

def work (force: Union[Vector2D, Vector1D, Vector3D], distance: Union[Vector2D, Vector1D, Vector3D]):
    return force.dotproduct(distance)

def area (vector1, vector2):
    return vector1.magnitude * vector2.magnitude * c.sin(angle_between(vector1, vector2))

def torque(vector1: Union[Vector2D, Vector3D], vector2: Union[Vector2D, Vector3D]):
    return vector1.crossproduct(vector2).magnitude

def xcomponent2D(res, theta):
    return res * c.cos(theta)

def ycomponent2D(res, theta):
    return res * c.sin(theta)

def resultant2D(x, y):
    return c.sqrt(x**2 + y**2)
