from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image
from math import sin, cos, degrees, radians, sqrt, pow, atan2
import math

print(GL_VERSION)
print(GL_MINOR_VERSION)
print(GL_MAJOR_VERSION)

width = 640
height = 480

primary = None
primary_rot_angle = 0
primary_rot_period_ms = 4000

secondary = None
secondary_rot_angle = 0
secondary_rev_angle = 90
secondary_rot_period_ms = 4000
secondary_rev_period_ms = 8000

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


def cart2sphe(x, y, z):
    rho_xy = sqrt(pow(x, 2)+pow(y, 2))
    rho = sqrt(pow(rho_xy, 2)+pow(z, 2))
    theta = atan2(z, rho_xy)
    print(x,y)
    phi = atan2(y, x)
    return rho, degrees(phi), degrees(theta)


def sphe2cart(rho, phi, theta):
    x = rho*sin(radians(theta))*cos(radians(phi))
    y = rho*sin(radians(theta))*sin(radians(phi))
    z = rho*cos(radians(theta))
    return x, y, z


def move_forward():
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta
    dx, dy, dz = sphe2cart(1., eye_phi, eye_theta)
    eye_x += dy
    eye_y += dz
    eye_z += dx


def move_backwards():
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta
    dx, dy, dz = sphe2cart(1., eye_phi, eye_theta)
    eye_x -= dy
    eye_y -= dz
    eye_z -= dx


def move_left():
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta
    dx, dy, dz, = sphe2cart(1., eye_phi+90, eye_theta)
    eye_x += dy
    eye_y += dz
    eye_z += dx


def move_right():
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta
    dx, dy, dz, = sphe2cart(1., eye_phi+90, eye_theta)
    eye_x -= dy
    eye_y -= dz
    eye_z -= dx


def get_look_at_args():
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta
    x, y, z = sphe2cart(eye_rho, eye_phi, eye_theta)
    target_x = eye_x + y
    target_y = eye_y + z
    target_z = eye_z + x
    # cosi sembra giusto
    up_z, up_x, up_y = sphe2cart(1, 0, eye_theta-90)

    # print(up_x,up_y,up_z)
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


def print_light_info(light_name):
    print(light_name.__repr__().split(" ")[0])
    print("\t->", GL_AMBIENT.__repr__().split(" ")[0], glGetLightfv(GL_LIGHT0, GL_AMBIENT))
    print("\t->", GL_DIFFUSE.__repr__().split(" ")[0], glGetLightfv(light_name, GL_DIFFUSE))
    print("\t->", GL_SPECULAR.__repr__().split(" ")[0], glGetLightfv(light_name, GL_SPECULAR))
    print("\t->", GL_POSITION.__repr__().split(" ")[0], glGetLightfv(light_name, GL_POSITION))
    print("\t->", GL_SPOT_DIRECTION.__repr__().split(" ")[0], glGetLightfv(light_name, GL_SPOT_DIRECTION))
    print("\t->", GL_SPOT_EXPONENT.__repr__().split(" ")[0], glGetLightfv(light_name, GL_SPOT_EXPONENT))
    print("\t->", GL_CONSTANT_ATTENUATION.__repr__().split(" ")[0], glGetLightfv(light_name, GL_CONSTANT_ATTENUATION))
    print("\t->", GL_LINEAR_ATTENUATION.__repr__().split(" ")[0], glGetLightfv(light_name, GL_LINEAR_ATTENUATION))
    print("\t->", GL_QUADRATIC_ATTENUATION.__repr__().split(" ")[0], glGetLightfv(light_name, GL_QUADRATIC_ATTENUATION))


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
    # glEnable(GL_LIGHT1)            # Enable light #1
    # glEnable(GL_LIGHT2)            # Enable light #2

    glLightfv(GL_LIGHT0, GL_POSITION, [-50.0, 0.0, +50.0])

    # reference for glLightModelfv parameters
    # https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/glLightModel.xml
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1])
    # GL_LIGHT_MODEL_AMBIENT
    # params contains four integer or floating-point values that specify the ambient RGBA intensity
    # of the entire scene.
    # Integer values are mapped linearly such that the most positive representable value maps to 1.0,
    # and the most negative representable value maps to -1.0 . Floating-point values are mapped directly.
    # Neither integer nor floating-point values are clamped.
    # The initial ambient scene intensity is (0.2, 0.2, 0.2, 1.0).
    # ....

    print_light_info(GL_LIGHT0)
    # print_light_info(GL_LIGHT1)
    # print_light_info(GL_LIGHT2)
    # print_light_info(GL_LIGHT3)

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

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)


def draw_axis_3d():

    global arrow_x_q, arrow_y_q, arrow_z_q

    glPushMatrix()
    # glTranslatef(eye_x, eye_y, eye_z)
    # glRotatef(eye_phi-180, 0., 1., 0.)
    # glRotatef(eye_theta-90, -1., 0., 0.)
    # glTranslatef(3.3, -2.5, 0)
    #
    # glDisable(GL_LIGHTING)
    # # three arrows are colored using glColor
    # # to do this light mus be disabled
    # # in this way arrows have theirs own color
    # # and doesn't have any effects on the rest of the scene
    #
    # glPushMatrix()
    # glTranslatef(0., 0., -5.)
    # glRotatef(90, 0., 1., 0.)
    # glColor3f(1., 0., 0.)
    # gluCylinder(arrow_x_q["cyl"], 0.1, 0.1, 0.3, 32, 32)
    # glTranslatef(0., 0., 0.3)
    # glutSolidCone(0.2, 0.5, 32, 32)
    # glPopMatrix()
    #
    # glPushMatrix()
    # glTranslatef(0., 0., -5.)
    # glRotatef(-90, 1., 0., 0.)
    # glColor3f(0., 1., 0.)
    # gluCylinder(arrow_y_q["cyl"], 0.1, 0.1, 0.3, 32, 32)
    # glTranslatef(0., 0., 0.3)
    # glutSolidCone(0.2, 0.5, 32, 32)
    # glPopMatrix()
    #
    # glPushMatrix()
    # glTranslatef(0., 0., -5.)
    # glColor3f(0., 0., 1.)
    # gluCylinder(arrow_z_q["cyl"], 0.1, 0.1, 0.3, 32, 32)
    # glTranslatef(0., 0., 0.3)
    # glutSolidCone(0.2, 0.5, 32, 32)
    # glPopMatrix()
    #
    # glEnable(GL_LIGHTING)

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


def draw_two_plate_tree():
    glPushMatrix()
    glRotatef(100, 0., 1., 0.)
    glRotatef(60, 1., 0., 0.)
    glTranslatef(0., 0., -2.9)
    draw_tree()
    glRotatef(90, 0., 0., 1.)
    draw_tree()
    glPopMatrix()


def draw_rose():

    glPushMatrix()
    glRotatef(-100, 0., 1., 0.)
    glRotatef(-60, 1., 0., 0.)
    glTranslatef(0., 0., -2.9)

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

    glPopMatrix()


def draw_little_prince_and_fox():

    glPushMatrix()
    glRotatef(-70, 0., 1., 0.)
    glRotatef(-30, 1., 0., 0.)
    glTranslatef(0., 0., -2.9)

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

    # glPushMatrix()
    # glTranslatef(*sun_pos)
    # glRotatef(90., 1., 0., 0.)
    # glEnable(GL_TEXTURE_2D)
    # glBindTexture(GL_TEXTURE_2D, tex_sun)
    # gluSphere(sun, 3, 32, 32)
    # glDisable(GL_TEXTURE_2D)
    # glPopMatrix()

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
    gluSphere(primary, 3, 32, 32)
    glDisable(GL_TEXTURE_2D)

    draw_two_plate_tree()

    draw_rose()

    draw_little_prince_and_fox()

    glPopMatrix()

    glPopMatrix()

    glRotatef(secondary_rev_angle, 0., 1., 0.)
    glTranslatef(0.0, 0.0, -6.)
    glRotatef(90., 1., 0., 0.)
    glRotatef(secondary_rot_angle, 0.0, 0., 1.0)

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (1, 1, 1, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.2, 0.2, 0.2, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0, 0, 0, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 10)

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_secondary_planet)
    gluSphere(secondary, 1, 32, 32)
    glDisable(GL_TEXTURE_2D)

    glPopMatrix()

    glFlush()


def keyboard(key, x, y):
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta
    global show_axis, block_rotation

    if key == b'\x1b':
        print("key ESC: exit")
        sys.exit()
    if key == b'w':
        move_forward()
        glutPostRedisplay()
        return
    if key == b's':
        move_backwards()
        glutPostRedisplay()
        return
    if key == b'a':
        move_left()
        glutPostRedisplay()
        return
    if key == b'd':
        move_right()
        glutPostRedisplay()
        return
    if key == b'0':
        eye_x = 0.
        eye_y = 0.
        eye_z = 0.
        eye_rho = 10.
        eye_phi = 180.
        eye_theta = 90.
        glutPostRedisplay()
        return
    # if key == b'9':
    #     sun_rho, sun_phi, sun_theta = cart2sphe(sun_pos[0], sun_pos[1], sun_pos[2])
    #     eye_rho = 10.
    #     eye_phi = -sun_theta
    #     eye_theta = sun_phi-90
    #     glutPostRedisplay()
    #     return
    if key == b'x':
        show_axis = not show_axis
        glutPostRedisplay()
        return
    if key == b'b':
        block_rotation = not block_rotation
        glutPostRedisplay()
        return


def special_keyboard(key, x, y):
    global eye_x, eye_y, eye_z
    global eye_rho, eye_phi, eye_theta

    # print(eye_rho, eye_phi, eye_theta)
    # print(*get_look_at_args())
    #
    if key == GLUT_KEY_LEFT:
        eye_phi += 1
        glutPostRedisplay()
        return
    if key == GLUT_KEY_RIGHT:
        eye_phi -= 1
        glutPostRedisplay()
        return
    if key == GLUT_KEY_DOWN:
        if eye_theta > 90+45:
            return
        eye_theta += 1
        glutPostRedisplay()
        return
    if key == GLUT_KEY_UP:
        if eye_theta < 90-45:
            return
        eye_theta -= 1
        glutPostRedisplay()
        return


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w / float(h), 1.0, 402.0)


def update_scene(val):
    global primary_rot_angle, primary_rot_period_ms
    global secondary_rot_angle, secondary_rev_angle, secondary_rot_period_ms, secondary_rev_period_ms
    global block_rotation

    if not block_rotation:
        primary_rot_angle += float(val)*360/primary_rot_period_ms
        secondary_rot_angle += float(val)*360/secondary_rot_period_ms
        secondary_rev_angle += float(val)*360/secondary_rev_period_ms

    glutTimerFunc(val, update_scene, val)
    glutPostRedisplay()
    return


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
# glutIdleFunc(display)

glutTimerFunc(10, update_scene, 10)

glutMainLoop()
