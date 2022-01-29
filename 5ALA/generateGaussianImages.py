from skimage import data, io, filters
from skimage.util import img_as_ubyte
from PIL import Image
import multiprocessing
import os
Image.MAX_IMAGE_PIXELS = None

ish_images = []
annotations = []
image_data_paths = []
gene_name = "CDCP1"
base_path = "images/{0}".format(gene_name)
for file_name in os.listdir(base_path):
    if "ISH" in file_name:
        ish_images.append(file_name)


def blur_image(image_path):
    ish_image = io.imread(base_path + "/" + image_path)
    ish_blurred = img_as_ubyte(filters.gaussian(ish_image, multichannel=True))
    io.imsave(base_path + "/" + image_path.split("_")[0] + "_blurred_" + image_path.split("_")[2] + ".jpg", ish_blurred)


if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=2)
    pool.map(blur_image, ish_images)
