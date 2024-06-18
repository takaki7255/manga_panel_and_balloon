import cv2
import numpy as np

# 幅1654,高さ1170の画像を作成
img = np.zeros((1170, 1654, 3), np.uint8)
# x = 46, y= 719の点に半径10の円を描画
cv2.circle(img, (46, 719), 10, (0, 255, 0), -1)
# x = 745, y =1166の点に半径10の円を描画
cv2.circle(img, (745, 1166), 10, (0, 0, 255), -1)
cv2.imshow("img", img)
cv2.waitKey(0)
cv2.waitKey()