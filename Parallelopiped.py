from vectors.Vector3D import Vector3D

class Parallelopiped:
    def __init__(self, length_vector, width_vector, height_vector):
        self.len = length_vector
        self.wid = width_vector
        self.hei = height_vector
        
    def volume(self):
        return abs(self.len.dotproduct(self.wid.crossproduct(self.hei)))
    
    