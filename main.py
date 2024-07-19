import requests
import music_tag
# In-built modules:
import re
import json
from pathlib import Path
import os
import logging
import argparse


from onep import onep


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


def get_work_id(
    user_input: str
) -> str | None:
    search = re.findall(r'\d+', str(user_input))
    if not search:
        return
    work_id = search[0]
    return work_id


def get_onsei_api(
    work_id: str
) -> list | dict:
    url = f'https://api.asmr.one/api/tracks/{work_id}'
    logging.info(f'Request: {url}')
    response = requests.get(url)
    # Ensure to get a valwork_id response
    response.raise_for_status()
    onsei_api = json.loads(response.content)
    return onsei_api


def tag_file(
    file_path: str | Path,
    cover_image: bytes,
    title: str,
    work_title: str
) -> None:
    f = music_tag.load_file(file_path)
    if not f:
        logging.error(f'Error loading file {file_path}')
        return
    f['title'] = title
    f['album'] = work_title
    f['tracknumber'] = onep(title)
    f['artwork'] = cover_image
    f.save()
    logging.info(f'Tagged file: {file_path}')


def download_media(
    file_path: Path,
    media_download_url: str
) -> bool:
    try:
        with open(file_path, 'xb') as file:
            file.write(requests.get(media_download_url).content)
        logging.info(f'Saved file: {file_path}')
    except FileExistsError:
        logging.info(f'File already exists: {file_path}')
        return False
    except Exception as e:
        logging.error(f'Error creating {file_path}: {e}')
        return False
    return True


def create_folder(
    folder_path: Path
) -> None:
    try:
        folder_path.mkdir(parents=True)
        logging.info(f'Created folder: {folder_path}')
    except FileExistsError:
        logging.info(f'Folder already exists: {folder_path}')
    except Exception as e:
        logging.error(f'Error creating folder {folder_path}: {e}')


def save_text_file(file_path: Path, media_stream_url: str) -> None:
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(requests.get(media_stream_url).text)


def save_cover_image(cover_path: Path, cover_image: bytes) -> None:
    cover_path.write_bytes(cover_image)
    logging.info(f'Saved cover: {cover_path}')


def process_file(
    onsei_api: dict,
    path: Path,
    cover_image: bytes,
    ignore: list
) -> None:
    file_type = onsei_api['type']
    media_download_url = onsei_api['mediaDownloadUrl']
    media_stream_url = onsei_api['mediaStreamUrl']
    extension = os.path.splitext(media_download_url)[1]

    if extension[1:] in ignore:
        return

    file_path = path / onsei_api['title']
    if file_type == 'text':
        save_text_file(file_path, media_stream_url)
    else:
        file_downloaded = download_media(file_path, media_download_url)
        if file_downloaded and file_type == 'audio':
            tag_file(
                file_path=file_path,
                cover_image=cover_image,
                title=os.path.splitext(onsei_api['title'])[0],
                work_title=onsei_api['workTitle']
            )
        cover_path = path / 'cover.jpg'
        if not cover_path.is_file():
            save_cover_image(cover_path, cover_image)


def recursive_download(
    onsei_api: list | dict,
    cover_image: bytes,
    path: Path = Path('.'),
    ignore: list[str] = []
) -> None:
    if 'error' in onsei_api:
        logging.error(onsei_api['error'])
        return
    # Folder/file list at a certain folder depth
    if isinstance(onsei_api, list):
        for element in onsei_api:
            recursive_download(
                element,
                cover_image,
                path,
                ignore
            )
    # Folder api dict
    elif onsei_api['type'] == 'folder':
        folder_name: str = onsei_api['title']
        # Don't create a folder if the folder name contains an ignored format
        if any(word.lower() in folder_name.lower() for word in ignore):
            return
        folder_path = path / folder_name
        create_folder(folder_path)
        recursive_download(
            onsei_api['children'],
            cover_image,
            folder_path,
            ignore
        )
    # File api dict
    else:
        process_file(onsei_api, path, cover_image, ignore)


def read_config(
    config_path: str
) -> dict:
    with open(config_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def fetch_cover_image(
    work_id: str
) -> bytes:
    cover_url = f'https://api.asmr-200.com/api/cover/{work_id}'
    response = requests.get(cover_url)
    response.raise_for_status()
    logging.info(f'Requested cover: {cover_url}')
    return response.content


def download_onsei(
    code: str
) -> None:
    config = read_config('config.json')
    work_id = get_work_id(code)
    if not work_id:
        logging.error('No work_id found in user input')
        return
    root_path = Path(config['rootPath']) / code
    ignore: list = config['ignore']
    root_path.mkdir(parents=True, exist_ok=True)
    logging.info(f'Created folder: {root_path}')
    try:
        cover_image = fetch_cover_image(work_id)
        onsei_api = get_onsei_api(work_id)
    except requests.exceptions.HTTPError as e:
        logging.error(e)
        return

    recursive_download(onsei_api, cover_image, root_path, ignore)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'codes', 
        help='The RJ/VJ codes of works you want to download.',
        nargs='?',
        default='',
        type=str
    )
    args = parser.parse_args()
    codes = args.codes
    if args.codes == '':
        codes: str = input('RJ/VJ code: ')
    for code in codes.split(','):
        download_onsei(code)
