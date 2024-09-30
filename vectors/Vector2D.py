from Vector1D import Vector1D
from Vector3D import Vector3D
import numpy as np
import cmath

class Vector2D(Vector1D):
    def __init__(self, x, y):
        super().__init__(x, 2)
        self.y = y
        self.magnitude = cmath.sqrt(x**2 + y**2)
        self.direction = cmath.atan2(y, x)
    
    def dotproduct(self, other) -> float:
        if type(other) is Vector2D:
            return self.x * other.x + self.y * other.y;
        else:
            return None
        
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0: return self
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def __str__(self):
        return f"<{self.x}, {self.y}>"
    
    def project(self, other):
        dot = self.dotproduct(other) / other.magnitude**2
        return self * dot
    
    def __pow__(self, scalar):
        return Vector2D(self.x**scalar, self.y**scalar)
    
    def project(self, other):
        dot = self.dotproduct(other) / other.magnitude**2
        return self * dot
    
    def extend(self):
        return Vector3D(self.x, self.y, 0)