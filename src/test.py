import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
from PIL import Image
import numpy as np

angle_y, angle_z, angle_sun = 0, 0, 0 # angles in degrees
H, W = 200, 200  # Sphere resolution
image = Image.open("map2.jpg").convert("RGB")
image_width, image_height = image.size
pixels = image.load()

def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    light_position = [5 * math.cos(math.radians(angle_sun)), 5 * math.sin(math.radians(angle_sun)), 0, 0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

# Equirectangular projection
def draw_sphere(radius, slices, stacks):
    setup_lighting()

    # Draw Sphere
    for i in range(stacks):
        lat0, lat1 = -math.pi * (-0.5 + i / stacks), -math.pi * (-0.5 + (i + 1) / stacks)
        z0, zr0, z1, zr1 = math.sin(lat0), math.cos(lat0), math.sin(lat1), math.cos(lat1)

        glBegin(GL_QUAD_STRIP)
        for j in range(slices + 1):
            lng = 2 * math.pi * (j / slices)
            x, y = math.cos(lng), math.sin(lng)

            img_x = int(j / slices * (image_width - 1))
            img_y0 = int(i / stacks * (image_height - 1))
            img_y1 = int((i + 1) / stacks * (image_height - 1))

            color0, color1 = pixels[img_x, img_y0], pixels[img_x, img_y1]

            glColor3f(*[c / 255 for c in color0])
            glNormal3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr0 * radius, y * zr0 * radius, z0 * radius)

            glColor3f(*[c / 255 for c in color1])
            glNormal3f(x * zr1, y * zr1, z1)
            glVertex3f(x * zr1 * radius, y * zr1 * radius, z1 * radius)
        glEnd()

    # Draw Axis (Z-axis Line Through the Sphere)
    glDisable(GL_LIGHTING)  # Disable lighting for a solid color line
    glColor3f(1, 0, 0)  # Red color for the axis

    glBegin(GL_LINES)
    glVertex3f(0, 0, -radius-0.5)  # Start at bottom of the sphere
    glVertex3f(0, 0, radius+0.5)  # End at top of the sphere
    glEnd()

    glEnable(GL_LIGHTING)  # Re-enable lighting


def correct_angles_to_lat_lon(angle_y, angle_z):
    lon = ((angle_z + 180) % 360) - 180
    lat = max(min(angle_y, 90), -90)
    return lat, lon

def map_pixel_to_sphere(i, j, width, height):
    """Maps pixel (i, j) to latitude/longitude, then converts to (x, y, z) coordinates on a unit sphere."""
    # Convert pixel coordinates to latitude (-π/2 to π/2) and longitude (-π to π)
    lat = math.pi * (j / height - 0.5)  # Latitude range: [-π/2, π/2]
    lon = 2 * math.pi * (i / width - 0.5)  # Longitude range: [-π, π]

    # Convert (lat, lon) to (x, y, z) on the sphere
    r = 1  # Unit sphere
    z = r * math.sin(lat)
    y = r * math.cos(lat) * math.sin(lon)
    x = r * math.cos(lat) * math.cos(lon)

    return x, y, z, lat, lon

def find_closest_quad(lat, lon, slices, stacks):
    closest_i = round((lat / math.pi + 0.5) * stacks)
    closest_j = round((lon / (2 * math.pi) + 0.5) * slices)
    img_x = min(max(int(closest_j / slices * (image_width - 1)), 0), image_width - 1)
    img_y = min(max(int(closest_i / stacks * (image_height - 1)), 0), image_height - 1)
    return pixels[img_x, img_y]

def generate_map_image(width, height):
    new_image = Image.new("RGB", (width, height))
    for i in range(width):
        for j in range(height):
            x, y, z, lat, lon = map_pixel_to_sphere(i, j, width, height)
            color = find_closest_quad(correct(lat-angle_y*math.pi/180.0,0.5*math.pi), correct(lon-angle_z*math.pi/180.0,math.pi), W, H)
            new_image.putpixel((i, j), color)
    new_image.show()



def display():
    global angle_y, angle_z, angle_sun
    angle_sun = (angle_sun + 1.5) % 360
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(-5, 0, 0, 0, 0, 0, 0, 0, 1)
    glRotatef(angle_y, 0, 1, 0)
    glRotatef(angle_z, 0, 0, 1)
    draw_sphere(1, W, H)
    glutSwapBuffers()

def keyboard(key, x, y):
    global angle_y, angle_z
    if key == b'w':
        angle_y -= 5
    elif key == b's':
        angle_y += 5
    elif key == b'a':
        angle_z -= 5
    elif key == b'd':
        angle_z += 5
    elif key == b'c': 
        generate_map_image(256, 128)
    
    angle_y,angle_z = correct_angles_to_lat_lon(angle_y=angle_y,angle_z=angle_z)    
    print("y ",angle_y," z ", angle_z)
    glutPostRedisplay()

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 1, 10)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(600, 600)
    glutCreateWindow(b"Navigable Earth")
    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glEnable(GL_DEPTH_TEST)
    glClearColor(0, 0, 0, 1)
    glutMainLoop()

if __name__ == "__main__":
    main()