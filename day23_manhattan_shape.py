#! /usr/bin/env python3
import cv2, numpy as np

s = 1000
r = 100
c = s // 2

im = np.zeros((s, s, 1), np.uint8)

ys, xs = np.unravel_index(np.arange(s * s).reshape((s, s)), (s, s))

mask = (abs(xs - c) + abs(ys - c) < r).reshape(s, s, 1)
#mask = ( (xs - c) ** 2 + (ys - c) ** 2 < 10000).reshape(s, s, 1)

im[mask] = 255

cv2.imwrite('shape.png', im)
