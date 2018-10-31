import cv2

image = cv2.imread("autojump.png", 3)
cv2.imshow("i", image)
cv2.waitKey()
cv2.destroyAllWindows()
