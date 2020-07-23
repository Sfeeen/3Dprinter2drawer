import cv2
import numpy as np

#everything in mm
STYLOS_X_OFFSET = 20
STYLOS_Y_OFFSET = 50
DRAW_X_OFFSET = 70
DRAW_Y_OFSSET = 70
PRINTER_DIM = 250
BACKUP_HEIGHT = 3
STYLUS_REL_NOZZLE_HEIGHT = 2
SPEED = 3600
MAX_DIM = PRINTER_DIM - STYLOS_Y_OFFSET

desired_img_width = 100
file = None

def scale_img(img, newsize_mm):

    width = img.shape[1]
    scale_percent = (newsize_mm * 10 / width) * 100  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    return resized

def show_img(img):
    cv2.imshow("image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def go_up():
    global file
    file.write('G0 Z' + str(BACKUP_HEIGHT + STYLUS_REL_NOZZLE_HEIGHT) + ';\n')

def go_down():
    global file
    file.write('G0 Z' + str(STYLUS_REL_NOZZLE_HEIGHT) + ';\n')

def move_to(x, y):
    global file
    x = x / 10.0
    y = y / 10.0
    x += STYLOS_X_OFFSET + DRAW_X_OFFSET
    y += STYLOS_Y_OFFSET + DRAW_Y_OFSSET
    file.write('G0 X' + str(x) + ' Y' + str(y) + ';\n')


def preprints():
    global file
    file = open("foto_bycontour.gcode", "w")
    file.write('G28;\n')
    file.write('G90;\n')
    file.write('G1 F' + str(SPEED) + ';\n')
    go_up()
    move_to(150, 150)
    go_down()
    file.write('M0 S30')
    go_up()
    go_up()


def line_by_line():
    global file
    preprints()

    previous_black = False
    for y in range(img.shape[1]):
        for x in range(img.shape[0]):
            if img[x, y] == 0:
                if not previous_black:
                    previous_black = True
                    move_to(x,y)
                    go_down()
            else:
                if previous_black:
                    previous_black = False
                    move_to(x,y)
                    go_up()
            if x == (img.shape[0] - 1):
                previous_black = False
                go_up()



def by_contour():
    global file
    preprints()

    contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST,
                                           cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[:-1]

    for c in contours:
        for coordinate in c:
            x = coordinate[0][0]
            y = coordinate[0][1]
            move_to(x, y)
            go_down()
        move_to(c[0][0][0], c[0][0][1])
        go_up()

def draw_layout(drawing):
    WHITE = (255, 255, 255)
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)

    blank_image = np.zeros((300, 300, 3), np.uint8)
    blank_image[:] = WHITE
    OFFSET = 20
    ORIGIN = (OFFSET, OFFSET + PRINTER_DIM)

    #printbed
    image = cv2.rectangle(blank_image, ORIGIN, ((OFFSET + PRINTER_DIM), (OFFSET)), BLUE, 1)
    cv2.putText(image, "printbed", (OFFSET, (OFFSET - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, BLUE)

    #printbereik
    image = cv2.rectangle(blank_image, ORIGIN, ((OFFSET + PRINTER_DIM - STYLOS_X_OFFSET), (OFFSET + STYLOS_Y_OFFSET)), GREEN, 1)
    cv2.putText(image, "tekenbereik", (OFFSET, (OFFSET + STYLOS_Y_OFFSET - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN)

    global desired_img_width
    drawing = scale_img(drawing, desired_img_width/10)
    draw_height = drawing.shape[0]
    draw_width = drawing.shape[1]
    drawing = cv2.cvtColor(drawing, cv2.COLOR_GRAY2RGB)

    image[OFFSET + PRINTER_DIM - draw_height - DRAW_Y_OFSSET:OFFSET + PRINTER_DIM - DRAW_Y_OFSSET,OFFSET + DRAW_X_OFFSET:OFFSET + draw_width + DRAW_X_OFFSET] = drawing

    image = scale_img(image, 80)
    show_img(image)


img = cv2.imread('pf.jpg', 0)
thresh = 50
img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)[1]
draw_layout(img)
img = scale_img(img, desired_img_width)
show_img(img)
img = cv2.flip(img, 0)

line_by_line()
#by_contour()








