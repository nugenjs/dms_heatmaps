# package json cv2, imutils

import cv2
import numpy as np
print("Hello, OpenCV!")
print(cv2.__version__)

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cv2.startWindowThread()



image = cv2.imread("./frame_Laser1.jpg") # is just a numpy array
# image = cv2.resize(image, (1280, 720))
# image = cv2.resize(image, (1920, 1080))
(h, w, d) = image.shape

# gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
# cv2.imshow("Image", gray)
# cv2.waitKey(0)

# roi = image[720:1240, 700:960]
# cv2.imshow("roi", roi)
# cv2.waitKey(0)

# (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)

boxes, weights = hog.detectMultiScale(image, winStride=(8,8))
# boxes, weights = hog.detectMultiScale(image, winStride=(8,8))

boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

for ( xA, yA, xB, yB) in boxes:
  cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)

cv2.imshow('image', image)



# terminal wait until keypress
cv2.waitKey(0)


  