from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image


arrow_x_q = {"cyl": None, "con": None}
arrow_y_q = {"cyl": None, "con": None}
arrow_z_q = {"cyl": None, "con": None}

width = 640
height = 480

primary = None
primary_rot_angle = 0

secondary = None
secondary_rot_angle = 0
secondary_rev_angle = 90

tex_primary_planet = None
tex_secondary_planet = None
tex_background = None
tex_tree = None

tex_primary_planet_path = "./img/mars.jpg"
tex_secondary_planet_path = "./img/mercury.jpg"
tex_background_path = "./img/mw.jpg"
tex_tree_path = "./img/tree.png"
tex_baobab_path = "./img/baobab.png"


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
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    return texture_id


def load_texture_x(file_name):
    return load_texture(file_name, "RGBA")


def init():

    global primary, secondary
    global tex_primary_planet, tex_secondary_planet, tex_tree, tex_background
    global arrow_x_q, arrow_y_q, arrow_z_q

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)

    tex_primary_planet = load_texture(tex_primary_planet_path)
    tex_secondary_planet = load_texture(tex_secondary_planet_path)
    tex_tree = load_texture_x(tex_tree_path)
    tex_background = load_texture(tex_background_path)

    primary = gluNewQuadric()
    gluQuadricNormals(primary, GLU_SMOOTH)
    gluQuadricTexture(primary, GL_TRUE)
    glEnable(GL_TEXTURE_2D)
    glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glDisable(GL_TEXTURE_2D)

    secondary = gluNewQuadric()
    gluQuadricNormals(secondary, GLU_SMOOTH)
    gluQuadricTexture(secondary, GL_TRUE)
    glEnable(GL_TEXTURE_2D)
    glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glDisable(GL_TEXTURE_2D)

    arrow_x_q["cyl"] = gluNewQuadric()
    gluQuadricNormals(primary, GLU_SMOOTH)
    gluQuadricTexture(primary, GL_TRUE)
    # arrow_x_q["con"] = gluNewQuadric()
    arrow_y_q["cyl"] = gluNewQuadric()
    gluQuadricNormals(primary, GLU_SMOOTH)
    gluQuadricTexture(primary, GL_TRUE)
    # arrow_y_q["con"] = gluNewQuadric()
    arrow_z_q["cyl"] = gluNewQuadric()
    gluQuadricNormals(primary, GLU_SMOOTH)
    gluQuadricTexture(primary, GL_TRUE)
    # arrow_z_q["con"] = gluNewQuadric()

    # glEnable(GL_BLEND)
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # glEnable(GL_ALPHA_TEST)
    # glAlphaFunc(GL_GREATER, 0.0)



def draw_axis():

    global arrow_x_q, arrow_y_q, arrow_z_q

    x_color = [1, 0, 0]     # X rosso
    y_color = [0, 1, 0]     # Y verde
    z_color = [0, 0, 1]     # Z blu

    glPushMatrix()
    glTranslatef(2.5, -2, 0)

    glPushMatrix()
    glTranslatef(0., 0., -5.)
    glRotatef(90, 0., 1., 0.)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, x_color)
    gluCylinder(arrow_x_q["cyl"], 0.1, 0.1, 0.5, 32, 32)
    glTranslatef(0., 0., 0.5)
    glutSolidCone(0.2, 0.5, 32, 32)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0., 0., -5.)
    glRotatef(-90, 1., 0., 0.)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, y_color)
    gluCylinder(arrow_y_q["cyl"], 0.1, 0.1, 0.5, 32, 32)
    glTranslatef(0., 0., 0.5)
    glutSolidCone(0.2, 0.5, 32, 32)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0., 0., -5.)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, z_color)
    gluCylinder(arrow_z_q["cyl"], 0.1, 0.1, 0.5, 32, 32)
    glTranslatef(0., 0., 0.5)
    glutSolidCone(0.2, 0.5, 32, 32)
    glPopMatrix()

    glPopMatrix()


def draw_background():
    glPushMatrix()

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_background)
    glBegin(GL_QUADS)
    glNormal3f(0.0, 0.0, 1.0)
    depth = 80.
    val_x = 0.90 * depth
    val_y = 0.60 * depth
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-val_x, -val_y, -depth)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-val_x, +val_y, -depth)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(+val_x, +val_y, -depth)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(+val_x, -val_y, -depth)
    glEnd()
    glDisable(GL_TEXTURE_2D)

    glPopMatrix()


def display():
    global primary_rot_angle, secondary_rot_angle, secondary_rev_angle

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()

    draw_axis()

    # draw_background()

    glFlush()


def keyboard(key, x, y):
    if key == b'\x1b':
        print("key ESC: exit")
        sys.exit()
    if key == b'w':
        print("key w: forwards")
        return
    if key == b's':
        print("key s: backwards")
        return
    if key == b'a':
        print("key a: left")
        return
    if key == b'd':
        print("key d: right")
        return
    if key == b'0':
        print("key 0: initial view")
        return


def special_keyboard(key, x, y):
    if key == GLUT_KEY_LEFT:
        print("key left:")
        return
    if key == GLUT_KEY_RIGHT:
        print("key right:")
        return
    if key == GLUT_KEY_DOWN:
        print("key down")
        return
    if key == GLUT_KEY_UP:
        print("key up:")
        return


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w / float(h), 1.0, 100.0)


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
