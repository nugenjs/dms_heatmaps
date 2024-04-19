
import cv2
import numpy as np

image = cv2.imread('frame_Laser1.jpg')


# Draw areas of interest on the image
#                   tl              tr          bl             br
laserArea = [[600, 380], [190, 430], [420, 1400], [1800, 1350]]
points = np.array([[600, 380], [190, 430], [420, 1400], [1800, 1350]], np.int32)
points = points.reshape((-1, 1, 2))
cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=5)

# draw a dot at the center of the image
dot1 = [960, 600]
# dot1 = [960, 720]
cv2.circle(image, (dot1[0], dot1[1]), 5, (255, 100, 255), -1)

# determine if the dot is inside the laser area
isInside = cv2.pointPolygonTest(points, (dot1[0], dot1[1]), False)
print('isInside:', isInside)


frame = cv2.imshow('image', image)
key = cv2.waitKey(0)
if key == 27:
    cv2.destroyAllWindows()
    print('Esc key pressed')
else:
    print('Key pressed:', key)
    cv2.destroyAllWindows()

print('End of program')


