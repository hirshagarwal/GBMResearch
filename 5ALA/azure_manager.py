import os
import pandas as pd
import numpy as np
from datetime import datetime
from PIL import Image
from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobClient
Image.MAX_IMAGE_PIXELS = None
from dotenv import load_dotenv

load_dotenv()
storage_account_name = "gbmresearch"
azure_key = os.getenv('AZURE_KEY')
azure_connection_string = os.getenv('AZURE_CONNECTION_STRING')


def upload_to_azure(gene_name, file_name):
    base_path = "images/auto{0}".format(gene_name)
    container_name = "auto{0}".format(gene_name.lower())
    blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    with open(base_path + "/" + file_name, "rb") as data:
        blob_client.upload_blob(data, connection_timeout=600)


def load_image_names(gene_name):
    container_name = "auto{0}".format(gene_name.lower())
    blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    blob_service_client.close()
    image_list = []
    for blob in blob_list:
        image_list.append(blob.name)
    return image_list


def get_blob(gene_name, blob_name):
    container_name = "auto{0}".format(gene_name.lower())
    blob = BlobClient.from_connection_string(conn_str=azure_connection_string, container_name=container_name, blob_name=blob_name)
    return blob.download_blob()


def get_image(gene_name, blob_name):
    container_name = "auto{0}".format(gene_name.lower())
    blob = BlobClient.from_connection_string(conn_str=azure_connection_string, container_name=container_name, blob_name=blob_name)
    img_bytes = BytesIO(blob.download_blob().content_as_bytes())
    return np.asarray(Image.open(img_bytes))


def save_results(gene_name, results):
    container_name = 'results'
    csv_file = results.to_csv(encoding='utf-8')
    dt = datetime.now()
    date_string = dt.strftime('%y-%m-%d-%H:%M')
    blob_name = "{0}-{1}.csv".format(date_string, gene_name)

    blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(csv_file)
