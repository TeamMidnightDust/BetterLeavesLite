from os import path
from tqdm import tqdm
import requests
import re

def downloadPack(input: str):
    if re.search("(http://*)|(https://*)", input) != None and input.endswith(".zip"):
        downloadZip(input)
    else:
        downloadFromModrinth(input)

def downloadFromModrinth(project_slug):
    response = requests.get(f'https://api.modrinth.com/v2/project/{project_slug}/version')
    latestFile = response.json()[0]['files'][0]
    latestFileURL = latestFile['url']
    if len(latestFileURL) < 1: raise Exception(f'Could not get the latest version URL for {project_slug}')
    downloadZip(latestFileURL, file_name=latestFile['filename'], pack_name=project_slug)

def downloadZip(url, file_name="", pack_name=""):
    download_stream = requests.get(url, stream=True)
    if file_name == "": file_name = url.split("/")[-1]
    if pack_name == "": pack_name = url
    file_path = 'input/texturepacks'

    print(f'Downloading texturepack: {pack_name} (Latest version: {file_name})')
    location = path.join(file_path, file_name)
    total = int(download_stream.headers.get('content-length', 0))
    with open(location, "wb") as handle, tqdm(
            unit="kB",
            desc=file_name,
            total=total,
            unit_scale=True,
            unit_divisor=1024,) as progressbar:
        for data in download_stream.iter_content(chunk_size=1024):
            size = handle.write(data)
            progressbar.update(size)
