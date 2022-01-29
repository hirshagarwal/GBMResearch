from skimage import data, io, filters
from skimage.color import rgb2hed, hed2rgb
from skimage.util import img_as_ubyte
from PIL import Image
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import azure_manager
Image.MAX_IMAGE_PIXELS = None


def compute_counts(path_args):
    gene_name = path_args[0]
    CORRELATION_PERCENT_PRECISION = 5
    
    print("Downloading: {0}".format(path_args[1]))
    
    # Read Images
    ish_image = azure_manager.get_image(gene_name, path_args[1])
    tumor_annotation_image = azure_manager.get_image(gene_name, path_args[2])

    print("Processing: {0}".format(path_args[1]))

    # Reshape Images
    if (ish_image.size < tumor_annotation_image.size):
        tumor_annotation_image = tumor_annotation_image[0:ish_image.shape[0], 0:ish_image.shape[1], :]
    if (ish_image.size > tumor_annotation_image.size):
        ish_image = ish_image[0:tumor_annotation_image.shape[0], 0:tumor_annotation_image.shape[1]]
    
    # Generate ISH mask
    # ish_mask = (ish_image[:, :, 0] < 220) & (ish_image[:, :, 1] > 200) & (ish_image[:, :, 2] > 180)
    # ish_mask = (np.abs(ish_image[:, :, 0] - 110) < 40) & (np.abs(ish_image[:, :, 1] - 110) < 40) & (np.abs(ish_image[:, :, 2] - 110) < 40)
    ish_mask = (np.abs(ish_image[:, :, 0] - 100) < 40) &\
               (np.abs(ish_image[:, :, 1] - 80) < 50) &\
               (np.abs(ish_image[:, :, 2]) < 150)

    # Tumor Annotation Regions
    leading_edge_mask = (tumor_annotation_image[:, :, 0] < 50) & (tumor_annotation_image[:, :, 1] > 100) & (tumor_annotation_image[:, :, 1] < 180) & (tumor_annotation_image[:, :, 2] > 150) & (tumor_annotation_image[:, :, 2] < 200)
    infiltrating_tumor_mask = (tumor_annotation_image[:, :, 0] > 200) & (tumor_annotation_image[:, :, 1] < 100) & (tumor_annotation_image[:, :, 2] > 100)
    cellular_tumor_mask = (tumor_annotation_image[:, :, 0] < 100) & (tumor_annotation_image[:, :, 1] > 200) & (tumor_annotation_image[:, :, 2] < 150)
    microvascular_proliferation_mask = (tumor_annotation_image[:, :, 0] > 200) & (tumor_annotation_image[:, :, 1] < 150) & (tumor_annotation_image[:, :, 2] < 150)
    necrosis_mask = (tumor_annotation_image[:, :, 0] < 50) & (tumor_annotation_image[:, :, 1] < 50) & (tumor_annotation_image[:, :, 2] < 50)
    perinecrotic_mask = (tumor_annotation_image[:, :, 0] < 80) & (tumor_annotation_image[:, :, 1] > 200) & (tumor_annotation_image[:, :, 2] > 230)
    
    # Compute Counts
    leading_edge_count = np.count_nonzero(np.logical_and(ish_mask, leading_edge_mask))
    infiltrating_tumor_count = np.count_nonzero(np.logical_and(ish_mask, infiltrating_tumor_mask))
    cellular_tumor_count = np.count_nonzero(np.logical_and(ish_mask, cellular_tumor_mask))
    microvascular_proliferation_count = np.count_nonzero(np.logical_and(ish_mask, microvascular_proliferation_mask))
    necrosis_count = np.count_nonzero(np.logical_and(ish_mask, necrosis_mask))
    perinecrotic_count = np.count_nonzero(np.logical_and(ish_mask, perinecrotic_mask))
    total_count = np.count_nonzero(ish_mask)
    
    # Compute Percents
    leading_edge_percent = round(leading_edge_count/(np.count_nonzero(leading_edge_mask) + 1) * 100, CORRELATION_PERCENT_PRECISION)
    infiltrating_tumor_percent = round(infiltrating_tumor_count/(np.count_nonzero(infiltrating_tumor_mask) + 1) * 100, CORRELATION_PERCENT_PRECISION)
    cellular_tumor_percent = round(cellular_tumor_count/(np.count_nonzero(cellular_tumor_mask) + 1) * 100, CORRELATION_PERCENT_PRECISION)
    microvascular_proliferation_percent = round(microvascular_proliferation_count/(np.count_nonzero(microvascular_proliferation_mask) + 1) * 100, CORRELATION_PERCENT_PRECISION)
    necrosis_percent = round(necrosis_count/(np.count_nonzero(necrosis_mask) + 1) * 100, CORRELATION_PERCENT_PRECISION)
    perinecrotic_percent = round(perinecrotic_count/(np.count_nonzero(perinecrotic_mask) + 1) * 100, CORRELATION_PERCENT_PRECISION)
    
    #print("Leading Edge:{0}({1}%)".format(leading_edge_count, round(leading_edge_count/total_count * 100, 3)))
    #print("Infiltrating Tumor:{0}({1}%)".format(infiltrating_tumor_count, round(infiltrating_tumor_count/total_count * 100, 3)))
    #print("Cellular Tumor:{0}({1}%)".format(cellular_tumor_count, round(cellular_tumor_count/total_count * 100, 3)))
    #print("Microvascular Proliferation:{0}({1}%)".format(microvascular_proliferation_count, round(microvascular_proliferation_count/total_count * 100, 3)))
    #print("Necrosis:{0}({1}%)".format(necrosis_count, round(necrosis_count/total_count * 100, 3)))
    print("Processed: {0}".format(path_args[1]))
    return [path_args[1], [leading_edge_percent, infiltrating_tumor_percent, cellular_tumor_percent, microvascular_proliferation_percent, necrosis_percent, perinecrotic_percent]]