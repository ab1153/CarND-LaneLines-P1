
#%%
#importing some useful packages
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2

#%%
#reading in an image
image = mpimg.imread('test_images/solidWhiteRight.jpg')
#printing out some stats and plotting
print('This image is:', type(image), 'with dimesions:', image.shape)
plt.imshow(image)  # if you wanted to show a single color channel image called 'gray', for example, call as plt.imshow(gray, cmap='gray')

#%%
import math

def grayscale(img):
    """Applies the Grayscale transform
    This will return an image with only one color channel
    but NOTE: to see the returned image as grayscale
    (assuming your grayscaled image is called 'gray')
    you should call plt.imshow(gray, cmap='gray')"""
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Or use BGR2GRAY if you read an image with cv2.imread()
    # return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
def canny(img, low_threshold, high_threshold):
    """Applies the Canny transform"""
    return cv2.Canny(img, low_threshold, high_threshold)

def gaussian_blur(img, kernel_size):
    """Applies a Gaussian Noise kernel"""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def region_of_interest(img, vertices):
    """
    Applies an image mask.
    
    Only keeps the region of the image defined by the polygon
    formed from `vertices`. The rest of the image is set to black.
    """
    #defining a blank mask to start with
    mask = np.zeros_like(img)   
    
    #defining a 3 channel or 1 channel color to fill the mask with depending on the input image
    if len(img.shape) > 2:
        channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
        ignore_mask_color = (255,) * channel_count
    else:
        ignore_mask_color = 255
        
    #filling pixels inside the polygon defined by "vertices" with the fill color    
    cv2.fillPoly(mask, vertices, ignore_mask_color)
    
    #returning the image only where mask pixels are nonzero
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

    
def draw_lines(img, lines, color=[255, 0, 0], thickness=2):
    """
    NOTE: this is the function you might want to use as a starting point once you want to 
    average/extrapolate the line segments you detect to map out the full
    extent of the lane (going from the result shown in raw-lines-example.mp4
    to that shown in P1_example.mp4).  
    
    Think about things like separating line segments by their 
    slope ((y2-y1)/(x2-x1)) to decide which segments are part of the left
    line vs. the right line.  Then, you can average the position of each of 
    the lines and extrapolate to the top and bottom of the lane.
    
    This function draws `lines` with `color` and `thickness`.    
    Lines are drawn on the image inplace (mutates the image).
    If you want to make the lines semi-transparent, think about combining
    this function with the weighted_img() function below
    """
    result = []
    left = []
    right = []

    # can be prove, the angel is only dependent on the height of camera mounted
    slopeThreshold = 0.5

    for line in lines:
        for x1,y1,x2,y2 in line:
            slope = (y2-y1) / (x2-x1)
            if slope > slopeThreshold:
                right.append((x1,y1))
                right.append((x2,y2))
            elif slope < -slopeThreshold:
                left.append((x1,y1))
                left.append((x2,y2))
    
    left_xs = np.array([x for (x,y) in left])
    left_ys = np.array([y for (x,y) in left])
    m, b = np.polyfit(left_xs, left_ys, 1)
    # determine the lower left
    x_candidate1 = np.amin(left_xs)
    y_candidate1 = x_candidate1 * m + b
    y_candidate2 = np.amax(left_ys)
    x_candidate2 = (y_candidate2 - b) / m
    if x_candidate1 < x_candidate2:
        x1 = x_candidate2
        y1 = y_candidate2
    else:
        x1 = x_candidate1
        y1 = y_candidate1
    # the upper right
    x_candidate1 = np.amax(left_xs)
    y_candidate1 = x_candidate1 * m + b
    y_candidate2 = np.amin(left_ys)
    x_candidate2 = (y_candidate2 - b) / m
    if x_candidate1 < x_candidate2:
        x2 = x_candidate2
        y2 = y_candidate2
    else:
        x2 = x_candidate1
        y2 = y_candidate1
    
    result.append((x1,y1,x2,y2))


    right_xs = np.array([x for (x,y) in right])
    right_ys = np.array([y for (x,y) in right])
    
    m, b = np.polyfit(right_xs, right_ys, 1)
    # determin the lower right
    x_candidate1 = np.amax(right_xs)
    y_candidate1 = x_candidate1 * m + b
    y_candidate2 = np.amax(right_ys)
    x_candidate2 = (y_candidate2 - b) / m
    if x_candidate1 < x_candidate2:
        x1 = x_candidate1
        y1 = y_candidate1
    else:
        x1 = x_candidate2
        y1 = y_candidate2
    
    # the upper left
    x_candidate1 = np.amin(right_xs)
    y_candidate1 = x_candidate1 * m + b
    y_candidate2 = np.amin(right_xs)
    x_candidate2 = (y_candidate2 - b) / m
    if x_candidate1 < x_candidate2:
        x2 = x_candidate1
        y2 = y_candidate1
    else:
        x2 = x_candidate2
        y2 = y_candidate2
    
    result.append((x1,y1,x2,y2))


    for line in result:
        x1,y1,x2,y2 = line
        x1 = int(round(x1))
        y1 = int(round(y1))
        x2 = int(round(x2))
        y2 = int(round(y2))

        cv2.line(img, (x1, y1), (x2, y2), color, thickness)


def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    """
    `img` should be the output of a Canny transform.
        
    Returns an image with hough lines drawn.
    """
    lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)
    line_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)

    draw_lines(line_img, lines, color=[255, 0, 0], thickness=7)
    return line_img

# Python 3 has support for cool math symbols.

def weighted_img(img, initial_img, α=0.8, β=1., λ=0.):
    """
    `img` is the output of the hough_lines(), An image with lines drawn on it.
    Should be a blank image (all black) with lines drawn on it.
    
    `initial_img` should be the image before any processing.
    
    The result image is computed as follows:
    
    initial_img * α + img * β + λ
    NOTE: initial_img and img must be the same shape!
    """
    return cv2.addWeighted(initial_img, α, img, β, λ)

#%%
# TODO: Build your pipeline that will draw lane lines on the test_images
# then save them to the test_images directory.
def process_image(img):
    w = img.shape[1]
    h = img.shape[0]
    gray = grayscale(img)
    blur = gaussian_blur(gray, 9)
    cannyEdges = canny(blur, 50, 150)
    lower_trapezoid = np.array([[0, h],[w, h], [0.6*w,0.6*h], [0.4*w, 0.6*h]], np.int)
    roi = region_of_interest(cannyEdges, [lower_trapezoid])
    hough_img = hough_lines(roi, 1, np.pi / 180, 15, 5, 5)
    result = weighted_img(hough_img, img, 1, 0.6)
    return result

import os
inDir = 'test_images'
outDir = 'test_images/out'
testFiles = os.listdir(inDir, )

for testFile in testFiles:
    if os.path.isdir(inDir + '/' + testFile):
        continue
    testImage = mpimg.imread(inDir + '/' + testFile)
    out = process_image(testImage)
    mpimg.imsave(outDir + '/' + testFile, out, cmap='gray')

print('completed')
#%%
# Import everything needed to edit/save/watch video clips
from moviepy.editor import VideoFileClip
from IPython.display import HTML

white_output = 'white.mp4'
clip1 = VideoFileClip("solidYellowLeft.mp4")
white_clip = clip1.fl_image(process_image) #NOTE: this function expects color images!!
%time white_clip.write_videofile(white_output, audio=False)