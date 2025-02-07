import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

angle = 0  # Rotation angle

def setup_lighting():
    """ Sets up OpenGL lighting. """
    glEnable(GL_LIGHTING)  # Enable lighting
    glEnable(GL_LIGHT0)    # Use the first light source

    # Light properties
    light_position = [1, 1, 1, 0]  # Directional light from (1,1,1)
    ambient_light = [0.2, 0.2, 0.2, 1.0]  # Soft ambient light
    diffuse_light = [0.8, 0.8, 0.8, 1.0]  # Strong white light
    specular_light = [1.0, 1.0, 1.0, 1.0]  # Specular highlights

    # Apply light properties
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)

    glEnable(GL_COLOR_MATERIAL)  # Allow object colors to interact with lighting
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Material properties
    mat_specular = [1.0, 1.0, 1.0, 1.0]
    mat_shininess = [50.0]  # Shininess factor
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

def draw_sphere(radius, slices, stacks):
    """ Renders a sphere with alternating stripes using triangle strips. """
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + (i / stacks))  # Latitude start
        lat1 = math.pi * (-0.5 + ((i + 1) / stacks))  # Latitude end
        z0, zr0 = math.sin(lat0), math.cos(lat0)  # Start ring
        z1, zr1 = math.sin(lat1), math.cos(lat1)  # End ring
        
        glBegin(GL_QUAD_STRIP)
        for j in range(slices + 1):
            lng = 2 * math.pi * (j / slices)  # Longitude
            x, y = math.cos(lng), math.sin(lng)

            # Stripe color pattern
            if i % 2 == 0:
                glColor3f(1, 1, 1)  # White stripe
            else:
                glColor3f(0, 0, 0)  # Black stripe
            
            glNormal3f(x * zr0, y * zr0, z0)  # Normal for lighting
            glVertex3f(x * zr0 * radius, y * zr0 * radius, z0 * radius)

            glNormal3f(x * zr1, y * zr1, z1)  # Normal for lighting
            glVertex3f(x * zr1 * radius, y * zr1 * radius, z1 * radius)
        glEnd()

def display():
    global angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)  # Camera setup

    glRotatef(angle, 0, 1, 0)  # Rotate sphere
    draw_sphere(1, 30, 30)  # Draw striped sphere

    glutSwapBuffers()
    angle += 0.25  # Increment rotation

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
    glutCreateWindow(b"Earth")

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(display)  # Animation
    glEnable(GL_DEPTH_TEST)

    glClearColor(0, 0, 0, 1)
    setup_lighting()
    glutMainLoop()

if __name__ == "__main__":
    main()
