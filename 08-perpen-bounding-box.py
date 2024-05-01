
from ultralytics import YOLO
import cv2
import numpy as np
from utils.perpendicular import calcPerpendicularSlopeLineIntercept
import sys

model = YOLO("yolov8m.pt")
image = cv2.imread('images/Laser1/2024-03-16-16-55-56_frame_Laser1.jpg')


# Process the image
results = model(image)
result = results[0]



# Draw areas of interest on the image
#                   tl              tr          bl             br
laserArea = [[600, 380], [190, 430], [420, 1400], [1800, 1350]]
points = np.array([[600, 380], [190, 430], [420, 1400], [1800, 1350]], np.int32)
points = points.reshape((-1, 1, 2))
cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=5)

# draw a line from the center of the top line to the center of the bottom line
lineStartX = int((laserArea[0][0]+laserArea[1][0]) / 2)
lineStartY = int((laserArea[0][1]+laserArea[1][1]) / 2)
lineEndX = int((laserArea[2][0]+laserArea[3][0]) / 2)
lineEndY = int((laserArea[2][1]+laserArea[3][1]) / 2) 

lineStartingPoint2 = (lineStartX, lineStartY)   
lineEndingPoint2 = (lineEndX, lineEndY)
# cv2.line(image, lineStartingPoint2, lineEndingPoint2, (255, 0, 0), 5)
cv2.arrowedLine(image, lineStartingPoint2, lineEndingPoint2, (255, 0, 0), 5, cv2.FILLED, 0, 0.03)


# find the slope intercept form of the line
m = (lineEndY - lineStartY) / (lineEndX - lineStartX)
b = lineStartY - (m * lineStartX)


# Process for all bounding boxes
bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
classes = np.array(result.boxes.cls.cpu(), dtype='int')

for cls, bbox in zip(classes, bboxes):
    # only humans
    if cls != 0:
        continue
    x1, y1, x2, y2 = bbox
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # create a point at bottom center of bounding box
    xMiddleFloat = ((x2+x1)/2)
    bbX = int(xMiddleFloat)
    bbY = int(y2)

    # draw a dot at the center of the bottom of each bounding box
    cv2.circle(image, (bbX, bbY), 5, (0, 0, 255), -1)

    # determine if the dot is inside the laser area
    isInside = cv2.pointPolygonTest(points, (bbX, bbY), False)
    print('isInside:', isInside)


    # find perpendicular
    interceptX, interceptY = calcPerpendicularSlopeLineIntercept(m, b, bbX, bbY)
    interceptDot = [int(interceptX), int(interceptY)] #expecting this number
    interceptDotNp = np.array([interceptDot], np.int32)
    cv2.circle(image, (interceptDot[0], interceptDot[1]), 5, (100, 100, 255), -1)
    cv2.line(image, interceptDot, [bbX, bbY], (255, 0, 0), 5)


    # calculate percentage from beginning to end of line of interest
    intInterceptX = int(interceptX)
    intInterceptY = int(interceptY)
    normalizedStart = lineStartX + lineStartY
    normalizedEnd = lineEndX + lineEndY
    normalizedIntercept = intInterceptX + intInterceptY
    linePercentageFromStart = (normalizedIntercept - normalizedStart) / (normalizedEnd - normalizedStart) * 100
    print('linePercentageFromStart', linePercentageFromStart)



frame = cv2.imshow('image', image)

key = cv2.waitKey(0)
if key == 27:
    cv2.destroyAllWindows()
    print('Esc key pressed')
else:
    print('Key pressed:', key)
    cv2.destroyAllWindows()

print('End of program')


