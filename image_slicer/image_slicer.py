from PIL import Image
import numpy as np


def slice_image_iterations(image, vstrips, hstrips, iterations):
    if iterations > 50:
        raise ValueError('Error : maximum number of iterations is 50')
    for i in range(0, iterations):
        image = slice_image(image, vstrips, hstrips)
    return image


def slice_image(image, vstrips, hstrips):

    if not isinstance(vstrips, int) or not isinstance(hstrips, int):
        raise ValueError('Error : vertical and horizontal strips must be integers')
    if vstrips <= 0 or hstrips <= 0:
        raise ValueError('Error : must have a positive number of vertical and horizontal strips')

    original_image_width = image.size[0]
    original_image_height = image.size[1]

    if vstrips > original_image_height or hstrips > original_image_width:
        raise ValueError('Error : number of strips must be less than or equal to number of pixels on an axis')

    # always need an even number of strips
    vstrips = vstrips if vstrips % 2 == 0 else vstrips + 1
    hstrips = hstrips if hstrips % 2 == 0 else hstrips + 1

    # cropping out pixels so image can be evenly split between strips
    cropped_image_width = np.floor_divide(original_image_width, hstrips) * hstrips
    cropped_image_height = np.floor_divide(original_image_height, vstrips) * vstrips

    # cropping out the central portion
    width_difference = original_image_width - cropped_image_width
    height_difference = original_image_height - cropped_image_height
    inner_box = (
        width_difference/2,
        height_difference/2,
        original_image_width - width_difference/2,
        original_image_height - height_difference/2)
    image = image.crop(inner_box)

    horiz_strip_width = cropped_image_width / hstrips
    vert_strip_height = cropped_image_height / vstrips

    strips = []
    for i in range(0, hstrips):
        strip_dims = (i * horiz_strip_width, 0, i * horiz_strip_width + horiz_strip_width, cropped_image_height)  # strip of image
        strips.append(image.crop(strip_dims))

    evens = np.array([np.asarray(s) for s in strips[::2]])
    odds = np.array([np.asarray(s) for s in strips[1::2]])
    total = Image.fromarray(np.hstack(np.concatenate((evens, odds))))

    strips = []
    for i in range(0, vstrips):
        strip_dims = (0, i * vert_strip_height, cropped_image_width, i * vert_strip_height + vert_strip_height)  # strip of image
        strips.append(total.crop(strip_dims))

    evens = np.array([np.asarray(s) for s in strips[::2]])
    odds = np.array([np.asarray(s) for s in strips[1::2]])
    return Image.fromarray(np.vstack(np.concatenate((evens, odds))))





