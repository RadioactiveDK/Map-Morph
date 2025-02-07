import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
from PIL import Image

angle_x, angle_y = 0, 0  # Rotation angles for navigation
H, W = 100, 200  # Number of stacks and slices
last_x, last_y = 0, 0  # Last mouse positions

# Load image
image = Image.open("map.jpg").convert("RGB")
image_width, image_height = image.size
pixels = image.load()

def setup_lighting():
    """ Sets up OpenGL lighting. """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    light_position = [1, 1, 1, 0]
    ambient_light = [0.2, 0.2, 0.2, 1.0]
    diffuse_light = [0.8, 0.8, 0.8, 1.0]
    specular_light = [1.0, 1.0, 1.0, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)


def draw_sphere(radius, slices, stacks):
    """ Renders a sphere with per-vertex coloring from the image. """
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + (i / stacks))
        lat1 = math.pi * (-0.5 + ((i + 1) / stacks))
        z0, zr0 = math.sin(lat0), math.cos(lat0)
        z1, zr1 = math.sin(lat1), math.cos(lat1)
        
        glBegin(GL_QUAD_STRIP)
        for j in range(slices + 1):
            lng = 2 * math.pi * (j / slices)
            x, y = math.cos(lng), math.sin(lng)

            img_x = int(j / slices * (image_width - 1))
            img_y0 = int(i / stacks * (image_height - 1))
            img_y1 = int((i + 1) / stacks * (image_height - 1))
            
            color0 = pixels[img_x, img_y0]
            color1 = pixels[img_x, img_y1]
            
            glColor3f(color0[0] / 255, color0[1] / 255, color0[2] / 255)
            glNormal3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr0 * radius, y * zr0 * radius, z0 * radius)

            glColor3f(color1[0] / 255, color1[1] / 255, color1[2] / 255)
            glNormal3f(x * zr1, y * zr1, z1)
            glVertex3f(x * zr1 * radius, y * zr1 * radius, z1 * radius)
        glEnd()


def display():
    global angle_x, angle_y
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)

    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    draw_sphere(1, W, H)

    glutSwapBuffers()


def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 1, 10)
    glMatrixMode(GL_MODELVIEW)


def mouse_motion(x, y):
    global last_x, last_y, angle_x, angle_y
    dx = x - last_x
    dy = y - last_y
    last_x, last_y = x, y
    
    angle_y += dx * 0.1  # Rotate left/right
    angle_x += dy * 0.1  # Rotate up/down
    glutPostRedisplay()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(600, 600)
    glutCreateWindow(b"Mouse Controlled Earth")

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMotionFunc(mouse_motion)
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0, 0, 0, 1)
    setup_lighting()
    
    glutMainLoop()


if __name__ == "__main__":
    main()
