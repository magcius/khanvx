
import cv2
import numpy as np

cap = cv2.VideoCapture('vid.mp4')

cursor_ = cv2.imread('cursor_1.png')

def expand_rect(rect, pad):
    return max(rect[0] - pad, 0), max(rect[1] - pad, 0), rect[2] + pad*2, rect[3] + pad*2

def find_cursor(frame, cursor):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, gray = cv2.threshold(gray, 127, 255, 0)
    nz = cv2.findNonZero(gray)
    if nz is None:
        return None

    br = cv2.boundingRect(nz)

    if br[2] < cursor.shape[1] or br[3] < cursor.shape[0]:
        return None

    br = expand_rect(br, 4)

    roi = frame[br[1]:br[1]+br[3], br[0]:br[0]+br[2]]
    res = cv2.matchTemplate(roi, cursor, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If there's no cursor, then we're done here.
    if min_val >= 1.0:
        return None

    # We found a cursor.
    top_left = min_loc[0] + br[0], min_loc[1] + br[1]

    cursor_size = cursor.shape[1::-1]
    bottom_right = (top_left[0] + cursor_size[0], top_left[1] + cursor_size[1])
    return cursor, top_left 

output = open('out.kvx', 'w')
output.write('KVX0\n')

def write_frame(cursor, cursor_pos, contours, color):
    output.write('\nFRM\n')
    output.write('CUR %d %d\n' % cursor_pos)
    output.write('COL %d %d %d\n' % color[:3])

    for contour in contours:
        output.write('CONT')
        for point in contour:
            output.write(' %d %d' % (point[0][0], point[0][1]))
        output.write('\n')

background = None

while True:
    ret, frame = cap.read()

    # If we don't yet have a background, 
    if background is None:
        background = frame
        last_foreground = background.copy()
        last_foreground.fill(0)
        continue

    foreground = cv2.subtract(frame, background)
    result = find_cursor(foreground, cursor_)

    # No cursor, so emit a black frame.
    if result is None:
        continue

    cursor, top_left = result

    cursor_size = cursor.shape[1::-1]
    bottom_right = (top_left[0] + cursor_size[0], top_left[1] + cursor_size[1])

    # Create an image of only the cursor.
    embedded_cursor = background.copy()
    embedded_cursor.fill(0)

    embedded_cursor[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = cursor

    foreground = cv2.subtract(foreground, embedded_cursor)
    cv2.rectangle(foreground, top_left, bottom_right, (0, 0, 255))

    diff = cv2.subtract(foreground, last_foreground)
    last_foreground = foreground

    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(foreground, contours, -1, (0, 255, 0), 3)
    cv2.imshow('f', foreground)
    cv2.waitKey(0)

    color = cv2.mean(foreground, thresh)

    write_frame(cursor, top_left, contours, color)

