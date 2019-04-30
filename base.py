from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image
from math import sin, cos, radians, sqrt, pow, atan2
import math

width = 640
height = 480

primary = None
primary_rot_angle = 0

secondary = None
secondary_rot_angle = 0
secondary_rev_angle = 90

sun = None
sun_pos = [-50.0, 0.0, +50.0]
sun_light = [1., 1, 1.]

sky_dome = None

tex_primary_planet = None
tex_secondary_planet = None
tex_background = None
tex_tree = None
tex_rose = None
tex_lp = None
tex_sun = None

tex_primary_planet_path = "./img/mars.jpg"
tex_secondary_planet_path = "./img/mercury.jpg"
tex_background_path = "./img/space.jpg"
tex_tree_path = "./img/tree.png"
tex_baobab_path = "./img/baobab.png"
tex_rose_path = "./img/rose.png"
tex_lp_path = "./img/lp.png"
tex_sun_path = "./img/sun.jpg"

block_rotation = True
show_axis = True


arrow_x_q = {"cyl": None, "con": None}
arrow_y_q = {"cyl": None, "con": None}
arrow_z_q = {"cyl": None, "con": None}


eye_x = 0.
eye_y = 0.
eye_z = 0.

eye_rho = 10.
eye_phi = 180.
eye_theta = 90.


def print_eye_info():
    print("Eye x, y, z: {}, {}, {}".format(eye_x, eye_y, eye_z))


def cart2sphe(x, y, z):
    rho_xy = sqrt(pow(x, 2)+pow(y, 2))
    rho = sqrt(rho_xy+pow(z, 2))
    theta = atan2(z, rho_xy)
    phi = atan2(y, x)
    return rho, phi, theta


def sphe2cart(rho, phi, theta):
    x = rho*sin(radians(theta))*cos(radians(phi))
    y = rho*sin(radians(theta))*sin(radians(phi))
    z = rho*cos(radians(theta))
    return x, y, z


def get_look_at_args():
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta
    x, y, z = sphe2cart(eye_rho, eye_phi, eye_theta)
    target_x = eye_x + y
    target_y = eye_y + z
    target_z = eye_z + x

    up_x, up_y, up_z = sphe2cart(1,eye_phi,eye_theta-90)
    up_x = 0.
    up_y = 1.
    up_z = 0.
    return eye_x, eye_y, eye_z, target_x, target_y, target_z, up_x, up_y, up_z


def load_texture(file_name, channels="RGBX"):

    image = Image.open(file_name)

    image_bytes = image.tobytes("raw", channels, 0, -1)

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # glPixelStorei(GL_UNPACK_ALIGNMENT,1)

    # http://pyopengl.sourceforge.net/documentation/manual-3.0/glTexImage2D.html
    # 0 ... specifies the level-of-detail number
    # 3 ... n of color
    # w ... width
    # h ... height
    # 0 ... border ... This value must be 0
    # image ... Specifies a pointer to the image data in memory
    glTexImage2D(
        GL_TEXTURE_2D,
        0, GL_RGBA, image.size[0], image.size[1], 0,
        GL_RGBA, GL_UNSIGNED_BYTE, image_bytes
    )

    # set the texture's stretching properties
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id


def load_texture_x(file_name):
    return load_texture(file_name, channels="RGBA")


def init():

    global primary, secondary, sun
    global tex_primary_planet, tex_secondary_planet, tex_tree, tex_background, tex_rose, tex_lp, tex_sun
    global arrow_x_q, arrow_y_q, arrow_z_q
    global sky_dome

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)            # Enable light #1
    glEnable(GL_LIGHT1)            # Enable light #1
    glEnable(GL_LIGHT2)            # Enable light #2

    # glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    # glLightModelfv(GL_LIGHT_MODEL_AMBIENT, light_ambient)

    glEnable(GL_NORMALIZE)

    tex_primary_planet = load_texture(tex_primary_planet_path)
    tex_secondary_planet = load_texture(tex_secondary_planet_path)
    tex_tree = load_texture_x(tex_baobab_path)
    tex_background = load_texture(tex_background_path)
    tex_rose = load_texture_x(tex_rose_path)
    tex_lp = load_texture_x(tex_lp_path)
    tex_sun = load_texture(tex_sun_path)

    primary = gluNewQuadric()
    gluQuadricNormals(primary, GLU_SMOOTH)
    gluQuadricTexture(primary, GL_TRUE)
    gluQuadricDrawStyle(primary, GLU_FILL)
    gluQuadricOrientation(primary, GLU_OUTSIDE)

    secondary = gluNewQuadric()
    gluQuadricNormals(secondary, GLU_SMOOTH)
    gluQuadricTexture(secondary, GL_TRUE)
    gluQuadricDrawStyle(secondary, GLU_FILL)
    gluQuadricOrientation(secondary, GLU_OUTSIDE)

    sun = gluNewQuadric()
    gluQuadricNormals(sun, GLU_SMOOTH)
    gluQuadricTexture(sun, GL_TRUE)
    gluQuadricDrawStyle(sun, GLU_FILL)
    gluQuadricOrientation(sun, GLU_OUTSIDE)

    arrow_x_q["cyl"] = gluNewQuadric()
    gluQuadricNormals(arrow_x_q["cyl"], GLU_SMOOTH)
    gluQuadricTexture(arrow_x_q["cyl"], GL_TRUE)

    arrow_y_q["cyl"] = gluNewQuadric()
    gluQuadricNormals(arrow_y_q["cyl"], GLU_SMOOTH)
    gluQuadricTexture(arrow_y_q["cyl"], GL_TRUE)

    arrow_z_q["cyl"] = gluNewQuadric()
    gluQuadricNormals(arrow_z_q["cyl"], GLU_SMOOTH)
    gluQuadricTexture(arrow_z_q["cyl"], GL_TRUE)

    sky_dome = gluNewQuadric()
    gluQuadricNormals(sky_dome, GLU_SMOOTH)
    gluQuadricTexture(sky_dome, GL_TRUE)
    gluQuadricDrawStyle(sky_dome, GLU_FILL)
    gluQuadricOrientation(sky_dome, GLU_INSIDE)

    # magimagia
    # glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    # glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)


def draw_axis_3d():

    global arrow_x_q, arrow_y_q, arrow_z_q

    x_color = [1, 0, 0]     # X rosso
    y_color = [0, 1, 0]     # Y verde
    z_color = [0, 0, 1]     # Z blu

    glPushMatrix()
    glTranslatef(eye_x, eye_y, eye_z)
    # x, y, z = sphe2cart(4, eye_phi-90, eye_theta+45)
    # glTranslatef(y, z, x)
    glTranslatef(2.5, -2, 0)

    glPushMatrix()
    glTranslatef(0., 0., -5.)
    glRotatef(90, 0., 1., 0.)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, x_color)
    glScalef(0.5, 0.5, 0.5)
    gluCylinder(arrow_x_q["cyl"], 0.1, 0.1, 0.3, 32, 32)
    glTranslatef(0., 0., 0.3)
    glutSolidCone(0.2, 0.5, 32, 32)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0., 0., -5.)
    glRotatef(-90, 1., 0., 0.)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, y_color)
    glScalef(0.5, 0.5, 0.5)
    gluCylinder(arrow_y_q["cyl"], 0.1, 0.1, 0.3, 32, 32)
    glTranslatef(0., 0., 0.3)
    glutSolidCone(0.2, 0.5, 32, 32)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0., 0., -5.)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, z_color)
    glScalef(0.5, 0.5, 0.5)
    gluCylinder(arrow_z_q["cyl"], 0.1, 0.1, 0.3, 32, 32)
    glTranslatef(0., 0., 0.3)
    glutSolidCone(0.2, 0.5, 32, 32)
    glPopMatrix()

    glPopMatrix()


def draw_tree():

    glPushMatrix()
    glScale(1.5, 1.5, 1.5)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0.0)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_tree)
    glBegin(GL_QUADS)
    glTexCoord2f(0., 0.)
    glVertex3f(-0.5, 0., 0.)
    glTexCoord2f(0., 1.)
    glVertex3f(-0.5, 0., -1.)
    glTexCoord2f(1., 1.)
    glVertex3f(+0.5, 0., -1.)
    glTexCoord2f(1., 0.)
    glVertex3f(+0.5, 0., 0.)
    glEnd()
    glDisable(GL_TEXTURE_2D)

    glDisable(GL_ALPHA_TEST)
    glDisable(GL_BLEND)

    glPopMatrix()


def draw_rose():

    glPushMatrix()
    glScale(0.75, 0.75, 0.75)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0.0)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_rose)
    glBegin(GL_QUADS)
    glTexCoord2f(0., 0.)
    glVertex3f(-0.5, 0., 0.)
    glTexCoord2f(0., 1.)
    glVertex3f(-0.5, 0., -1.)
    glTexCoord2f(1., 1.)
    glVertex3f(+0.5, 0., -1.)
    glTexCoord2f(1., 0.)
    glVertex3f(+0.5, 0., 0.)
    glEnd()
    glDisable(GL_TEXTURE_2D)

    glDisable(GL_ALPHA_TEST)
    glDisable(GL_BLEND)

    glPopMatrix()


def draw_lp():

    glPushMatrix()
    glScale(0.75, 0.75, 0.75)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0.0)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_lp)
    glBegin(GL_QUADS)
    glTexCoord2f(0., 0.)
    glVertex3f(-0.5, 0., 0.)
    glTexCoord2f(0., 1.)
    glVertex3f(-0.5, 0., -1.)
    glTexCoord2f(1., 1.)
    glVertex3f(+0.5, 0., -1.)
    glTexCoord2f(1., 0.)
    glVertex3f(+0.5, 0., 0.)
    glEnd()
    glDisable(GL_TEXTURE_2D)

    glDisable(GL_ALPHA_TEST)
    glDisable(GL_BLEND)

    glPopMatrix()


def draw_background():
    global sky_dome, tex_background
    glPushMatrix()

    glRotatef(90., 1., 0., 0.)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_background)
    gluSphere(sky_dome, 200, 512, 512)
    glDisable(GL_TEXTURE_2D)

    glPopMatrix()


def display():
    global primary_rot_angle, secondary_rot_angle, secondary_rev_angle

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()

    gluLookAt(
        *get_look_at_args()
    )

    if show_axis:
        draw_axis_3d()

    draw_background()

    glPushMatrix()
    glTranslatef(*sun_pos)
    glRotatef(90., 1., 0., 0.)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_sun)
    # glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
    # glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (1, 1, 1, 1))
    # glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.2, 0.2, 0.2, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, sun_light)
    # glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 10)
    gluSphere(sun, 3, 32, 32)
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

    glPushMatrix()

    glTranslatef(0.0, 0.0, -10.)

    glPushMatrix()

    glRotatef(90., 1., 0., 0.)

    glPushMatrix()
    glRotatef(-20., 1., 0., 0.)
    glRotatef(-10., 0., 1., 0.)
    glRotatef(primary_rot_angle, 0.0, 0., 1.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_primary_planet)
    # glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
    # glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (1, 1, 1, 1))
    # glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.2, 0.2, 0.2, 1))
    # glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0, 0, 0, 1))
    # glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 10)
    gluSphere(primary, 3, 32, 32)
    glDisable(GL_TEXTURE_2D)

    glPushMatrix()
    glRotatef(100, 0., 1., 0.)
    glRotatef(60, 1., 0., 0.)
    glTranslatef(0., 0., -2.9)
    draw_tree()
    glRotatef(90, 0., 0., 1.)
    draw_tree()
    glPopMatrix()

    glPushMatrix()
    glRotatef(-100, 0., 1., 0.)
    glRotatef(-60, 1., 0., 0.)
    glTranslatef(0., 0., -2.9)
    draw_rose()
    glPopMatrix()

    glPushMatrix()
    glRotatef(-70, 0., 1., 0.)
    glRotatef(-30, 1., 0., 0.)
    glTranslatef(0., 0., -2.9)
    draw_lp()
    glPopMatrix()

    glPopMatrix()

    glPopMatrix()

    glRotatef(secondary_rev_angle, 0., 1., 0.)
    glTranslatef(0.0, 0.0, -6.)
    glRotatef(90., 1., 0., 0.)
    glRotatef(secondary_rot_angle, 0.0, 0., 1.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_secondary_planet)

    # glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
    # glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (1, 1, 1, 1))
    # glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.2, 0.2, 0.2, 1))
    # glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0, 0, 0, 1))
    # glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 10)

    gluSphere(secondary, 1, 32, 32)
    glDisable(GL_TEXTURE_2D)

    glPopMatrix()

    if not block_rotation:
        primary_rot_angle += 1
        secondary_rot_angle += 2
        secondary_rev_angle += 1

    glFlush()


def keyboard(key, x, y):
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta
    global show_axis, block_rotation
    if key == b'\x1b':
        print("key ESC: exit")
        sys.exit()
    if key == b'w':
        print("key w: forwards")
        dx, dy, dz = sphe2cart(1., eye_phi, eye_theta)
        eye_x += dy
        eye_y += dz
        eye_z += dx
        print_eye_info()
        return
    if key == b's':
        print("key s: backwards")
        dx, dy, dz, = sphe2cart(1., eye_phi, eye_theta)
        eye_x -= dy
        eye_y -= dz
        eye_z -= dx
        print_eye_info()
        return
    if key == b'a':
        print("key a: left")
        dx, dy, dz, = sphe2cart(1., eye_phi+90, eye_theta)
        eye_x += dy
        eye_y += dz
        eye_z += dx
        print_eye_info()
        return
    if key == b'd':
        print("key d: right")
        dx, dy, dz, = sphe2cart(1., eye_phi+90, eye_theta)
        eye_x -= dy
        eye_y -= dz
        eye_z -= dx
        print_eye_info()
        return
    if key == b'0':
        print("key 0: initial view")
        eye_x = 0.
        eye_y = 0.
        eye_z = 0.
        eye_rho = 10.
        eye_phi = 180.
        eye_theta = 90.
        return
    if key == b'x':
        print("key x: toggle 3D axis")
        show_axis = not show_axis
        return
    if key == b'b':
        print("key b: toggle rotation")
        block_rotation = not block_rotation
        return


def special_keyboard(key, x, y):
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta
    if key == GLUT_KEY_LEFT:
        eye_phi += 1
        print("key left:")
        return
    if key == GLUT_KEY_RIGHT:
        print("key right:")
        eye_phi -= 1
        return
    if key == GLUT_KEY_DOWN:
        print("key down")
        if eye_theta == 135:
            return
        eye_theta += 1
        return
    if key == GLUT_KEY_UP:
        print("key up:")
        if eye_theta == 45:
            return
        eye_theta -= 1
        return


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w / float(h), 1.0, 402.0)


glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA | GLUT_ALPHA | GLUT_DEPTH)
glutInitWindowSize(width, height)
glutInitWindowPosition(0, 0)
glutCreateWindow("Lil")

init()

glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(special_keyboard)
glutIdleFunc(display)

glutMainLoop()

#########################################


def draw_axis_2d():
    axis_len = 0.05
    x_color = [1, 0, 0]
    y_color = [0, 1, 0]
    z_color = [0, 0, 1]

    glPushMatrix()

    glTranslatef(.7, -.5, .0)

    # X
    glColor3f(*x_color)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, x_color)
    glBegin(GL_LINES)
    glVertex3f(-axis_len, 0, -1)
    glVertex3f(axis_len, 0, -1)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(axis_len, 0, -1)
    glVertex3f(axis_len * 9. / 10, axis_len * 1. / 10, -1)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(axis_len, 0, -1)
    glVertex3f(axis_len * 9. / 10, -axis_len * 1. / 10, -1)
    glEnd()

    # Y
    glColor3f(*y_color)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, y_color)
    glBegin(GL_LINES)
    glVertex3f(0, -axis_len, -1)
    glVertex3f(0, axis_len, -1)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(0, axis_len, -1)
    glVertex3f(axis_len * 1. / 10, axis_len * 9. / 10, -1)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(0, axis_len, -1)
    glVertex3f(-axis_len * 1. / 10, axis_len * 9. / 10, -1)
    glEnd()

    # Z
    glColor3f(*z_color)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, z_color)
    glBegin(GL_LINES)
    glVertex3f(0, 0, -axis_len)
    glVertex3f(0, 0, axis_len)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(0, 0, axis_len)
    glVertex3f(axis_len * 1. / 10, 0, axis_len * 9. / 10)
    glEnd()
    glBegin(GL_LINES)
    glVertex3f(0, 0, axis_len)
    glVertex3f(-axis_len * 1. / 10, 0, axis_len * 9. / 10)
    glEnd()

    glPopMatrix()
