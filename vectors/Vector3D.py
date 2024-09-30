from Vector1D import Vector1D
import cmath

class Vector3D(Vector1D):
    def __init__(self, x, y, z):
        super().__init__(x, 3)
        self.y = y
        self.z = z
        self.magnitude = cmath.sqrt(x**2 + y**2 + z**2)
        self.direction = cmath.atan2(y, x)
        
    def dotproduct(self, other) -> float:
        if type(other) is Vector1D:
            return self.x * other.x + self.y * other.y + self.z * other.z;
        else:
            return None
    def crossproduct(self, other):
        if type(other) is Vector3D:
            return Vector3D(self.y * other.z - self.z * other.y,
                          self.z * other.x - self.x * other.z,
                          self.x * other.y - self.y * other.x)
        else:
            return None
    def __add__(self, other):
        if type(other) is Vector3D:
            return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return None
        
    def __sub__(self, other):
        if type(other) is Vector3D:
            return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            return None
        
    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
        
    def __truediv__(self, scalar):
        if scalar != 0:
            return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)
        else:
            raise ZeroDivisionError("Division by zero")
    def __str__(self):
        return f"<{self.x}, {self.y}, {self.z}>"
    
    def __pow__(self, scalar):
        return Vector3D(self.x**scalar, self.y**scalar, self.z**scalar)
    
    def project(self, other):
        dot = self.dotproduct(other) / other.magnitude**2
        return self * dot