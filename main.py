import requests
import music_tag
# In-built modules:
import re
import json
from pathlib import Path, WindowsPath
import os
import logging

from onep import onep


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


def get_id(user_input: str) -> int | None:
    search = re.findall(r'\d+', str(user_input))
    if not search:
        return
    id = search[0]
    return id


def get_onsei_api(
    id: int
) -> list | dict:
    url = f'https://api.asmr.one/api/tracks/{id}'
    logging.info(f'Request: {url}')
    response = requests.get(url)
    onsei_api = json.loads(response.content)
    return onsei_api


def tag_file(
    file_path: str | WindowsPath,
    cover: bytes,
    title: str,
    work_title: str
) -> None:
    f = music_tag.load_file(file_path)
    f['title'] = title
    f['album'] = work_title
    f['tracknumber'] = onep(title)
    f['artwork'] = cover
    f.save()
    logging.info(f'Tagged file: {file_path}')


def recursive_download(
    onsei_api: list | dict,
    cover: bytes,
    path: WindowsPath = Path('.'),
    ignore: list = []
) -> None:
    if 'error' in onsei_api:
        logging.error(onsei_api['error'])
        return
    elif isinstance(onsei_api, list):
        for element in onsei_api:
            recursive_download(
                onsei_api=element,
                cover=cover,
                path=path,
                ignore=ignore
            )
    # Dict
    elif onsei_api['type'] == 'folder':
        folder_name = onsei_api['title']
        folder_path: Path = path / folder_name
        # Don't create a folder if the folder name contains an ignored format
        if all(word not in folder_name for word in ignore):
            folder_path.mkdir(parents=True, exist_ok=True)
            logging.info(f'Created folder: {folder_path}')
            recursive_download(
                onsei_api=onsei_api['children'],
                cover=cover,
                path=folder_path,
                ignore=ignore
            )
    else:
        type = onsei_api['type']
        media_download_url = onsei_api['mediaDownloadUrl']
        media_stream_url = onsei_api['mediaStreamUrl']
        extension = os.path.splitext(media_download_url)[1]

        if extension[1:] in ignore:
            return
        file_path: WindowsPath = path / onsei_api['title']
        # To not output gibberish in .txt files like readme
        if type == 'text':
            with open(file_path, 'w', encoding="utf-8") as file:
                file.write(requests.get(media_stream_url).text)
        else:
            with open(file_path, 'wb') as file:
                file.write(requests.get(media_download_url).content)
                if type == 'audio':
                    tag_file(
                        file_path=file_path,
                        cover=cover,
                        title=os.path.splitext(onsei_api['title'])[0],
                        work_title=onsei_api['workTitle']
                    )
                    # Save cover.jpg in the audio folders (for jellyfin)
                    cover_path = path / 'cover.jpg'
                    if not os.path.isfile(cover_path):
                        with open(cover_path, 'wb') as cover_file:
                            cover_file.write(cover)
                        logging.info(f'Saved cover: {cover_path}')
        logging.info(f'Saved file: {file_path}')


def complete_download(user_input: str) -> None:
    # Read the config file
    with open('config.json', 'r') as file:
        config = json.load(file)
    # Set all the variables
    root_path: WindowsPath = Path(config['rootPath']) / user_input
    ignore: list = config['ignore']
    root_path.mkdir(parents=True, exist_ok=True)
    logging.info(f'Created folder: {root_path}')
    id = get_id(user_input)
    cover_url = f'https://api.asmr-200.com/api/cover/{id}'
    cover = requests.get(cover_url).content
    logging.info(f'Request cover: {cover_url}')
    # Get the API
    onsei_api = get_onsei_api(id)
    # Download the files
    recursive_download(onsei_api, cover, root_path, ignore)


if __name__ == '__main__':
    user_input: str = input('RJ/VJ code: ')
    complete_download(user_input)
