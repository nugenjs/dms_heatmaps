# package json cv2, imutils

import cv2
print("Hello, OpenCV!")
print(cv2.__version__)

image = cv2.imread("./frame_Laser1.jpg") # is just a numpy array
(h, w, d) = image.shape

print("width={}, height={}, depth={}".format(w, h, d))


# cv2.imshow("Image", image)
# cv2.waitKey(0)



# beginCords = (700, 1240)
# endCords = (960, 720)

# roi = image[720:1240, 700:960]
roi = image[720:1240, 700:960]
cv2.imshow("roi", roi)
cv2.waitKey(0)