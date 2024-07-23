import cv2
import os

img = cv2.imread("./スクリーンショット 2024-07-15 17.22.44.png")
bin = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, bin = cv2.threshold(bin, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# 白黒比
print((bin == 255).sum() / (bin == 0).sum())
cv2.imwrite("output.jpg", bin)
