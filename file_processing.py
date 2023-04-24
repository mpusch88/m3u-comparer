import os
import sys
import urllib.parse
from tqdm import tqdm
from utils import extract_audio_metadata, scan_folder_for_audio_files
from settings import errors_file_name


def find_matching_and_similar_files(list1, list2, strict_mode):
    matching_files = []
    similar_files = []
    added_pairs = set()

    for item1 in tqdm(list1, desc='Finding matching and similar files'):
        for item2 in list2:
            if metadata_matches(item1, item2, strict_mode):
                pair_key = frozenset([item1['file_name'], item2['file_name']])
                if item1["file_name"] == item2["file_name"] and pair_key:
                    matching_files.append((item1, item2))
                elif pair_key not in added_pairs:
                    similar_files.append((item1, item2))
                    # avoids copying the same file twice - possibly move elsewhere to add pairs to txt file
                    added_pairs.add(pair_key)

    return matching_files, similar_files


def metadata_matches(item1, item2, strict_mode):
    match_count = 0

    if item1["title"] == item2["title"] and item1["title"]:
        match_count += 1
    if item1["artist"] == item2["artist"] and item1["artist"]:
        match_count += 1
    if item1["album"] == item2["album"] and item1["album"]:
        match_count += 1
    if item1["bitrate"] == item2["bitrate"]:
        match_count += 1

    if strict_mode == False:
        return match_count >= 3 and round(item1["length"], 2) == round(item2["length"], 2)

    else:
        return match_count >= 4 and round(item1["length"], 2) == round(item2["length"], 2)


def compare_metadata_lists(list1, list2, strict_mode):
    missing_in_list1 = []
    missing_in_list2 = []

    for item in tqdm(list2, desc='Comparing first list'):
        if not any(metadata_matches(item, input1, strict_mode) for input1 in list1):
            missing_in_list1.append(item)

    print()

    for item in tqdm(list1, desc='Comparing second list'):
        if not any(metadata_matches(item, input2, strict_mode) for input2 in list2):
            missing_in_list2.append(item)

    print()
    return missing_in_list1, missing_in_list2


def process_input(input_path, recursive):
    if os.path.isfile(input_path) and (input_path.lower().endswith('.m3u8') or input_path.lower().endswith('.m3u')):
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        return extract_files_with_metadata(lines)

    elif os.path.isdir(input_path):
        audio_files = []
        audio_files = scan_folder_for_audio_files(input_path, recursive)

        files_with_metadata = []

        for file_path in tqdm(audio_files, desc=f'Processing {input_path}'):
            metadata = extract_audio_metadata(file_path)

            if metadata:
                file_data = {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "title": metadata.get("title"),
                    "artist": metadata.get("artist"),
                    "album": metadata.get("album"),
                    "length": metadata.get("length"),
                    "bitrate": metadata.get("bitrate")
                }

                files_with_metadata.append(file_data)

            # else:
            #     with open(errors_file_name, "a", encoding='utf-8') as error_file:
            #         error_file.write(
            #             f"Error processing {file_path}: Invalid audio file\n")

        return files_with_metadata
    else:
        print(f"Error: Invalid input path: {input_path}")
        sys.exit(1)


def extract_files_with_metadata(lines):
    files_with_metadata = []

    for line in lines:
        if not line.startswith("#") and not "#EXTM3U" in line:
            line = line.strip()
            line = urllib.parse.unquote(line)
            line = line.replace("file:///", "")

            file_path = os.path.normpath(line).replace("\\", "/")

            if os.path.isfile(file_path):
                metadata = extract_audio_metadata(file_path)

                if metadata:
                    file_data = {
                        "file_path": file_path,
                        "file_name": os.path.basename(file_path),
                        "title": metadata.get("title"),
                        "artist": metadata.get("artist"),
                        "album": metadata.get("album"),
                        "length": metadata.get("length"),
                        "bitrate": metadata.get("bitrate")
                    }

                    files_with_metadata.append(file_data)

                # else:
                #     with open(errors_file_name, "a", encoding='utf-8') as error_file:
                #         error_file.write(
                #             f"Error processing {file_path}: Invalid audio file\n")

            else:
                with open(errors_file_name, "a", encoding='utf-8') as error_file:
                    error_file.write(
                        f"Error processing {file_path}: File does not exist\n")

    return files_with_metadata
