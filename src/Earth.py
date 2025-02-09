import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
from PIL import Image
import numpy as np

angle_y, angle_z, angle_sun = 0, 0, 0 # angles in degrees
H, W = 200, 200  # Sphere resolution
image = Image.open("tissot.png").convert("RGB") # Map image to load
image_width, image_height = image.size
pixels = image.load()

# Sun and ambient light
def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    light_position = [5 * math.cos(math.radians(angle_sun)), 5 * math.sin(math.radians(angle_sun)), 0, 0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

# Equirectangular projection of Map on Sphere
def draw_sphere(radius, slices, stacks):
    setup_lighting()

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

    # Draw Axis of Earth
    glDisable(GL_LIGHTING)
    glColor3f(1, 0, 0)

    glBegin(GL_LINES)
    glVertex3f(0, 0, -radius-0.5)
    glVertex3f(0, 0, radius+0.5) 
    glEnd()

    glEnable(GL_LIGHTING)

# Find effective latitude and longitude for the new map
def effective_lat_lon(lat1, lon1, lat2, lon2):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Convert (lat2, lon2) to Cartesian coordinates (x, y, z)
    x = math.cos(lat2) * math.cos(lon2)
    y = math.cos(lat2) * math.sin(lon2)
    z = math.sin(lat2)

    # Rotate around Y-axis (latitude offset)
    x_prime = x * math.cos(lat1) + z * math.sin(lat1)
    y_prime = y
    z_prime = -x * math.sin(lat1) + z * math.cos(lat1)

    # Rotate around Z-axis (longitude offset)
    x_double_prime = x_prime * math.cos(lon1) - y_prime * math.sin(lon1)
    y_double_prime = x_prime * math.sin(lon1) + y_prime * math.cos(lon1)
    z_double_prime = z_prime

    # Convert back to latitude and longitude
    if(z_double_prime<-1):
        z_double_prime = -1
    lat_new = math.asin(z_double_prime)
    lon_new = math.atan2(y_double_prime, x_double_prime)

    # Convert back to degrees
    return math.degrees(lat_new), math.degrees(lon_new)

# Find color at (lat, lon) in the map
def find_pixel_color(lat, lon, slices, stacks):
    closest_i = round((lat / math.pi + 0.5) * stacks)
    closest_j = round((lon / (2 * math.pi) + 0.5) * slices)
    img_x = min(max(int(closest_j / slices * (image_width - 1)), 0), image_width - 1)
    img_y = min(max(int(closest_i / stacks * (image_height - 1)), 0), image_height - 1)
    return pixels[img_x, img_y]

# Origin translation on Equirectangular mapping
def generate_map_image(width, height):
    new_image = Image.new("RGB", (width, height))
    for i in range(width):
        for j in range(height):
            # Convert pixel to sphere coordinates
            lat2 = math.pi * (j / height - 0.5)
            lon2 = 2 * math.pi * (i / width - 0.5)
            
            # Correct the latitude and longitude using the rotation
            lat_corrected, lon_corrected = effective_lat_lon(-angle_y, -angle_z, math.degrees(lat2), math.degrees(lon2))
            
            # Convert back to radians for lookup
            lat_corrected = math.radians(lat_corrected)
            lon_corrected = math.radians(lon_corrected)
            
            # Find the closest texture color from the map image
            color = find_pixel_color(lat_corrected, lon_corrected, W, H)
            
            new_image.putpixel((i, j), color)
    
    new_image.show()

# Display/Idle function
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

# Keyboard events
def keyboard(key, x, y):
    global angle_y, angle_z
    if key == b'w':
        angle_y -= 5
    elif key == b's':
        angle_y += 5
    elif key == b'a':
        angle_z += 5
    elif key == b'd':
        angle_z -= 5
    elif key == b'c': 
        generate_map_image(512, 256)
    
    # Standardize the angles
    lon = ((angle_z + 180) % 360) - 180
    lat = max(min(angle_y, 90), -90)

    print("y ",angle_y," z ", angle_z)
    glutPostRedisplay()

# Window reshape function
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