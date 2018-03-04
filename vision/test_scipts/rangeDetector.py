# Name: Arnav Garg

import cv2
import argparse
from operator import xor

def callback(value):
    pass

def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)
    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255
        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)

def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)
    return values

def main(camera):
    range_filter = 'RGB'
    setup_trackbars(range_filter)
    while True:
        ret, image = camera.read()
        if not ret:
            break
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)
        thresh = cv2.inRange(image, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
        cv2.imshow("Original", image)
        cv2.imshow("Thresh", thresh)
        if cv2.waitKey(1) & 0xFF is ord('q'):
            print('Min: [{}, {}, {}]'.format(v1_min, v2_min, v3_min))
            print('Max: [{}, {}, {}]'.format(v1_max, v2_max, v3_max))
            cv2.destroyAllWindows()
            break

camera = cv2.VideoCapture(0)
main(camera)