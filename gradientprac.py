import cv2
import numpy as np
import matplotlib.pyplot as plt

def compute_gradients(image):
  # padded_image = np.pad(image, ((1,1), (1,1)), mode='edge')

  # dx_filter = np.array([[-1,0,1], [-1,0,1], [-1,0,1]])
  # dy_filter = np.array([[-1,-1,-1], [0,0,0], [1,1,1]])

  # gradient_x = cv2.filter2D(padded_image, -1, dx_filter)
  # gradient_y = cv2.filter2D(padded_image, -1, dy_filter)
  # # remove padding 
  # gradient_x = gradient_x[1:-1, 1:-1]
  # gradient_y = gradient_y[1:-1, 1:-1]

  padded_image = np.pad(image, ((1,1), (1,1)), mode='edge')

  dx_filter = np.array([[-1,0,1], [-2,0,2], [-1,0,1]])
  dy_filter = np.array([[-1,-2,-1], [0,0,0], [1,2,1]])

  gradient_x = cv2.filter2D(padded_image, -1, dx_filter)
  gradient_y = cv2.filter2D(padded_image, -1, dy_filter)

  return gradient_x, gradient_y

image = cv2.imread('frame_MetalShop2.jpg', cv2.IMREAD_GRAYSCALE)

# gradient_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
# gradient_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)

gradient_x, gradient_y = compute_gradients(image)


plt.subplot(1,3,1)
plt.imshow(image, cmap='gray')
plt.title('og')
plt.axis('off')

plt.subplot(1,3,2)
plt.imshow(gradient_x, cmap='gray')
plt.title('grade on x')
plt.axis('off')

plt.subplot(1,3,3)
plt.imshow(gradient_y, cmap='gray')
plt.title('grade on y')
plt.axis('off')

plt.show()



