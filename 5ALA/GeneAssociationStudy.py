import multiprocessing
from multiprocessing import set_start_method
import azure_manager
import azure_computation
import sys
import pandas as pd
import numpy as np


def run_gene_analysis():
    base_path = "image/auto{0}".format(gene_name)
    files = azure_manager.load_image_names(gene_name)

    ish_images = []
    annotations = []
    image_data_paths = []

    for file_name in files:
        if "Annotation" in file_name:
            annotations.append(file_name)
        if "ISH" in file_name:
            ish_images.append(file_name)

    for file_name in ish_images:
        split_name = file_name.split("ISH")[0]
        for annotation_name in annotations:
            annotation_split = annotation_name.split("Annotation")[0]
            if annotation_split == split_name:
                image_data_paths.append((gene_name, file_name, annotation_name))

    if samples_to_run > 0:
        image_data_paths = image_data_paths[:samples_to_run]

    print("Running computation on {0} samples with {1} CPUs".format(len(image_data_paths), multiprocessing.cpu_count()))

    with multiprocessing.Pool(multiprocessing.cpu_count(), maxtasksperchild=1) as pool:
        results = pool.map_async(azure_computation.compute_counts, image_data_paths)
        print("Done processing")
        pool.close()
        pool.join()

    print("Computation Complete - Processing and saving data...")

    region_labels = np.array(['leading_edge', 'infiltrating_tumor', 'cellular_tumor', 'vascular', 'necrosis', 'perinecrotic'])
    region_correlation = pd.DataFrame(columns=region_labels)
    for result in results.get():
        region_correlation.loc[result[0]] = result[1]
    azure_manager.save_results(gene_name, region_correlation)
    print(region_correlation)


if __name__ == "__main__":
    set_start_method("spawn")
    gene_name = sys.argv[1]
    samples_to_run = 0
    if len(sys.argv) > 2:
        samples_to_run = int(sys.argv[2])
    run_gene_analysis()
