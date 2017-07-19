from __future__ import print_function, division

import numpy as np
from scipy import interpolate


def cart2pol(x, y):
    """Convert cartesian coordinates to polar coordinates.
    x, y = pol2cart(theta, rho)"""
    rho = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    return theta, rho

def pol2cart(theta, rho):
    """Convert polar coordinates to cartesian coordinates.
    x, y = pol2cart(theta, rho)"""
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y

def imgpolarcoord(img):
    """
    Convert a given image from cartesian coordinates to polar coordinates.

    Image center:
    The center of rotation of a 2D image of dimensions xdim x ydim is defined by 
    ((int)xdim/2, (int)(ydim/2)) (with the first pixel in the upper left being (0,0).
    Note that for both xdim=ydim=65 and for xdim=ydim=64, the center will be at (32,32).
    This is the same convention as used in SPIDER and XMIPP. Origin offsets reported 
    for individual images translate the image to its center and are to be applied 
    BEFORE rotations.
    """
    row, col = img.shape
    cx = int(col/2)
    cy = int(row/2)
    radius = float(min([row-cy, col-cx, cx, cy]))
    angle = 360.0
    # Interpolation: Nearest
    pcimg = np.zeros((int(radius), int(angle)))
    radius_range = np.arange(0, radius, 1)
    angle_range = np.arange(0, 2*np.pi, 2*np.pi/angle)
    i = 0
    for r in radius_range:
        j = 0
        for a in angle_range:
            pcimg[i, j] = img[int(cy+round(r*np.sin(a))), int(cx+round(r*np.cos(a)))]
            j = j + 1
        i = i + 1
    return pcimg

def imgpolarcoord3(img):
    """
    converts a given image from cartesian coordinates to polar coordinates.

    Image center:
    The center of rotation of a 2D image of dimensions xdim x ydim is defined by 
    ((int)xdim/2, (int)(ydim/2)) (with the first pixel in the upper left being (0,0).
    Note that for both xdim=ydim=65 and for xdim=ydim=64, the center will be at (32,32).
    This is the same convention as used in SPIDER and XMIPP. Origin offsets reported 
    for individual images translate the image to its center and are to be applied 
    BEFORE rotations.
    """
    row, col = img.shape
    cx = int(col/2)
    cy = int(row/2)
    radius = float(min([row-cy, col-cx, cx, cy]))
    print(radius)
    angle = 360.0
    # Interpolation: Linear (undone)
    x_range = np.arange(-radius+1, radius, 1)
    y_range = np.arange(-radius+1, radius, 1)
    z = img[1:int(cy+radius),1:int(cx+radius)]
    # f = interpolate.interp2d(x_range, y_range, img[1:int(cy+radius),1:int(cx+radius)], kind='linear')
    # f = interpolate.RectBivariateSpline(x_range, y_range, img[1:int(cy+radius),1:int(cx+radius)])
    f = interpolate.interp2d(x_range, y_range, z, kind='linear')

    theta_range = np.arange(0, 2*np.pi, 2*np.pi/angle)
    rho_range = np.arange(0, radius, 1)
    theta_grid, rho_grid = np.meshgrid(theta_range, rho_range)
    new_x_grid, new_y_grid = pol2cart(theta_grid, rho_grid)

    plt.figure(3)
    plt.imshow(new_x_grid)
    plt.figure(4)
    plt.imshow(new_y_grid)
    plt.show()

    # pcimg = f(new_x_grid.ravel(), new_y_grid.ravel())
    # pcimg = pcimg.reshape((int(radius+1),-1))
    pcimg = np.zeros((int(radius), int(angle)))
    print(pcimg.shape)
    return pcimg

def get_corr_img(img, pcimg_interpolation='nearest'):
    """
    get a angular correlation image
    """
    if 'nearest' in pcimg_interpolation.lower():
        pcimg = imgpolarcoord(img)
    elif 'linear' in pcimg_interpolation.lower():
        pcimg = imgpolarcoord3(img)

    pcimg_fourier = np.fft.fftshift(np.fft.fft(pcimg, axis=1))
    corr_img = np.fft.ifft(np.fft.ifftshift(pcimg_fourier*np.conjugate(pcimg_fourier)), axis=1)
    return corr_img.real


if __name__ == '__main__':
    from cryoio import mrc
    from matplotlib import pyplot as plt
    map_file = '../particle/EMD-2325.map'
    model = mrc.readMRC(map_file)
    proj1 = np.sum(model, axis=2)
    corr_img = get_corr_img(proj1, pcimg_interpolation='linear')
    plt.figure(1)
    plt.imshow(proj1)
    # plt.figure(2)
    # plt.imshow(c2_img)
    plt.show()
