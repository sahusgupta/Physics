import cmath
import numpy as np

from vectors import Vector3D

class Vector1D:
    def __init__(self, x, dims):
        self.dims = dims
        self.x: float = x
        self.magnitude: float = cmath.sqrt(x**2)
        self.direction: float = cmath.atan2(0)
        
    
    def __dotproduct__(self, other) -> float:
        if type(other) is Vector1D:
            return self.x * other.x;
        else:
            return None
        
    def __add__(self, other):
        return Vector1D(self.x + other.x)
    
    def __sub__(self, other):
        return Vector1D(self.x - other.x)
    
    def __mul__(self, scalar):
        return Vector1D(self.x * scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0: return self
        return Vector1D(self.x / scalar)
    
    def __str__(self):
        return f"<{self.x}>"
    
    def __pow__(self, scalar):
        return Vector1D(self.x**scalar)
    
    def project(self, other):
        dot = self.dotproduct(other) / other.magnitude**2
        return self * dot
    
    def extend(self):
        return Vector3D(self.x, 0, 0)