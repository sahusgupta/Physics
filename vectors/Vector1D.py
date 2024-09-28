import cmath
import numpy as np

class Vector1D:
    def __init__(self, x, dims):
        self.dims = dims
        self.x = x
        self.magnitude = property(cmath.sqrt(x**2))
        self.direction = property(lambda: cmath.atan2(0))
        
    
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