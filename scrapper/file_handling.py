import os
import subprocess
from urllib.parse import urlparse


def download_file(url, destination):
    """
    Download a file from the specified URL and save it to the provided destination.

    :param url: The URL of the file to download.
    :param destination: The path where the file should be saved.
    """

    file_name = os.path.basename(urlparse(url).path)
    # Join the destination path with the file name
    destination = os.path.join(destination, file_name)

    cmd = ['curl', '-L', '-A', "Mozilla/5.0", '-o', destination, url]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def create_dir(path):
    """
    Create a directory
    :param path: The path of the directory
    """

    # If the directory does not exist, then it is created. If it already exists, this function does nothing.
    if not os.path.exists(path):
        os.makedirs(path)
