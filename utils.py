import os
import glob
import shutil
from tqdm import tqdm
from tinytag import TinyTag, TinyTagException
from settings import errors_file_name


def clear_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "w", encoding='utf-8') as file:
            file.write("")


def copy_possible_duplicates(duplicates, folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    for index, (item1, item2) in enumerate(tqdm(duplicates, desc="Copying possible duplicates"), start=1):
        new_dir = os.path.join(folder_path, str(index))
        os.makedirs(new_dir, exist_ok=True)

        shutil.copy2(item1["file_path"], os.path.join(
            new_dir, item1["file_name"]))
        shutil.copy2(item2["file_path"], os.path.join(
            new_dir, item2["file_name"]))


def extract_audio_metadata(file_path):
    metadata = {}

    try:
        audio = TinyTag.get(file_path)
        metadata["title"] = audio.title if audio.title else "Unknown"
        metadata["artist"] = audio.artist if audio.artist else "Unknown"
        metadata["album"] = audio.album if audio.album else "Unknown"
        metadata["length"] = audio.duration if audio.duration else 0
        metadata["bitrate"] = audio.bitrate if audio.bitrate else 0

    except TinyTagException as e:
        with open(errors_file_name, "a", encoding='utf-8') as error_file:
            error_file.write(f"Error processing {file_path}: {e}\n")

    return metadata


def scan_folder_for_audio_files(folder_path, recursive):
    audio_files = []

    for ext in ('*.mp3', '*.m4a', '*.flac', '*.wav', '*.ogg'):
        if recursive:
            files = glob.glob(os.path.join(
                folder_path, '**', ext), recursive=True)
        else:
            files = glob.glob(os.path.join(folder_path, ext))

        audio_files.extend(files)

    return audio_files
