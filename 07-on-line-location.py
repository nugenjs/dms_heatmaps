
import cv2
import numpy as np

image = cv2.imread('images/Laser1/2024-03-16-16-55-56_frame_Laser1.jpg')


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
cv2.line(image, lineStartingPoint2, lineEndingPoint2, (255, 0, 0), 5)

print('lineStartX:', lineStartX)
print('lineStartY:', lineStartY)
print('lineEndX:', lineEndX)
print('lineEndY:', lineEndY)

# find the slope intercept form of the line
# y = mx + b
# m = (y2 - y1) / (x2 - x1)
# b = y - mx
m = (lineEndY - lineStartY) / (lineEndX - lineStartX)
b = lineStartY - (m * lineStartX)
print('m:', m)
print('b:', b)

# find the perpendicular line
mPerpendicular = -1 / m
bPerpendicular = 0
print('mPerpendicular:', mPerpendicular)
print('bPerpendicular:', bPerpendicular)




# draw a dot at the center of the image
# dot1 = [960, 600]
# dot1 = [350, 350]
# dot1 = [1310, 1375]
dot1 = [900, 300]
dot1Np = np.array([dot1], np.int32)
cv2.circle(image, (dot1[0], dot1[1]), 5, (0, 0, 255), -1)

# determine if the dot is inside the laser area
isInside = cv2.pointPolygonTest(points, (dot1[0], dot1[1]), False)
print('isInside:', isInside)











# m = (y2 - y1) / (x2 - x1)

#y = mx+b
#y2 = m2x+b2

# m2 = -.74
# b2 = 300 - -(1/1.3566433566433567)900 => 964


# y1 = 1.4*x+-130
# y2 = -.74*x+964

# 1.4*x-130 = -.74*x+964
# 1.4x+.74x = 964+130
# 2.14x = 1090
# x=1090/2.14

secondm = -(1/m)
secondb = dot1[1] - (secondm*dot1[0])
print('secondm', secondm)
print('secondb', secondb)

print('###################')
print(secondb - b)
print(m - secondm)

interceptx = (secondb - b) / (m - secondm)
intercepty = secondm * interceptx + secondb

print('interceptx', interceptx)
print('intercepty', intercepty)

intinterceptx = int(interceptx)
intintercepty = int(intercepty)

interceptDot = [intinterceptx, intintercepty] #expecting this number
interceptDotNp = np.array([interceptDot], np.int32)
cv2.circle(image, (interceptDot[0], interceptDot[1]), 15, (100, 100, 255), -1)

cv2.line(image, interceptDot, dot1, (255, 0, 0), 5)


# calculate percentage from beginning to end of line of interest
normalizedStart = lineStartX + lineStartY
normalizedEnd = lineEndX + lineEndY
normalizedIntercept = intinterceptx + intintercepty
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


