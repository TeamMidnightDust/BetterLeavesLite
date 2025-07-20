from os import path
from tqdm import tqdm
import requests

def downloadFromModrinth(project_slug):
    response = requests.get(f'https://api.modrinth.com/v2/project/{project_slug}/version')
    latestFile = response.json()[0]['files'][0]
    latestFileURL = latestFile['url']
    if len(latestFileURL) < 1: raise Exception(f'Could not get the latest version URL for {project_slug}')

    download_stream = requests.get(latestFileURL, stream=True)
    file_name = latestFile['filename']
    file_path = 'input/texturepacks'

    print(f'Downloading texturepack: {project_slug} (Latest version: {file_name})')
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
