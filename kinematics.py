from vectors.Vector2D import Vector2D
from vectors.Vector3D import Vector3D
import cmath as c


def vel_time2D(vox, voy, ax, ay, t):
    return Vector2D(vox + ax * t, voy + ay * t)

def vel_time3D(vox, voy, vz, ax, ay, az, t):
    return Vector3D(vox + ax * t, voy + ay * t, vz + az * t)

def pos_time2D(xo, yo, vox, voy, t, ax, ay):
    return Vector2D(xo + vox * t + ax * (t**2), yo + voy * t + ay * (t**2))

def pos_time3D(xo, yo, zo, vox, voy, voz, t, ax, ay, az):
    return Vector3D(xo + vox * t + ax * (t**2), yo + voy * t + ay * (t**2), zo + voz * t + az * (t**2))

def vel_pos2D(vox, ax, dx, voy, ay, dy):
    return Vector2D(c.sqrt(vox ** 2 + 2*ax*dx), c.sqrt(voy ** 2 + 2*ay*dy))

def vel_pos3D(vox, ax, dx, voy, ay, dy, voz, az, dz):
    return Vector3D(c.sqrt(vox ** 2 + 2*ax*dx), c.sqrt(voy ** 2 + 2*ay*dy), c.sqrt(voz ** 2 + 2*az*dz))

