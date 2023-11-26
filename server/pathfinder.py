from typing import Tuple

import numpy as np
import cv2
import pyastar2d

cutoff_fxn = np.vectorize(lambda x: np.inf if x == 0 else 1)


def generate_img_with_path(source_file: str, destination_file: str,
                           start_tuple: Tuple[int, int],
                           end_tuple: Tuple[int, int]):
    image = cv2.imread(source_file)

    # smaller1 = cv2.resize(image, None, fx=0.75, fy=0.75, interpolation=cv2.INTER_AREA)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # blurred = cv2.bilateralFilter(gray, 9, 300, 300)
    # dilated = cv2.dilate(blurred, None, iterations=3)

    blurred = cv2.bilateralFilter(gray, 9, 100, 100)
    dilated = cv2.dilate(blurred, None, iterations=1)

    _, thresholded_image = cv2.threshold(dilated, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(thresholded_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(thresholded_image, contours, -1, (0, 255, 0), 3)

    weights = cutoff_fxn(thresholded_image)
    weights = weights.astype(np.float32)

    path = pyastar2d.astar_path(weights, start_tuple, end_tuple, allow_diagonal=False)

    # thresholded_image = cv2.cvtColor(thresholded_image, cv2.COLOR_GRAY2RGB)

    # Red color in BGR
    color = (0, 0, 255)

    start_tuple = (start_tuple[1], start_tuple[0])
    end_tuple = (end_tuple[1], end_tuple[0])

    image = cv2.circle(image, start_tuple, 15, color, -1)
    image = cv2.circle(image, end_tuple, 15, color, -1)

    for temp in path:
        i, j = temp
        image = cv2.circle(image, (j, i), 3, color, -1)

    cv2.imwrite(destination_file, image)
