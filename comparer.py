#!/usr/bin/env python3

import os
import sys
import glob
import shutil
import urllib.parse
from tinytag import TinyTag, TinyTagException


def find_matching_files(list1, list2): #, strict_mode):
    matching_files = []

    for item1 in list1:
        for item2 in list2:
            if metadata_matches(item1, item2) and item1["file_name"] != item2["file_name"]:  #, strict_mode)
                matching_files.append((item1, item2))

    return matching_files


def metadata_matches(item1, item2): #, strict_mode):
    match_count = 0

    if item1["title"] == item2["title"] and item1["title"]:
        match_count += 1
    if item1["artist"] == item2["artist"] and item1["artist"]:
        match_count += 1
    if item1["album"] == item2["album"] and item1["album"]:
        match_count += 1
    if item1["bitrate"] == item2["bitrate"]:
        match_count += 1

    # if strict_mode == False:
    return match_count >= 3 and round(item1["length"], 2) == round(item2["length"], 2)

    # else:
    #     return match_count >= 4 and round(item1["length"], 2) == round(item2["length"], 2)


def compare_metadata_lists(list1, list2): #, strict_mode):
    missing_in_list1 = [item for item in list2 if not any(
        metadata_matches(item, input1) for input1 in list1)] #, strict_mode)
    missing_in_list2 = [item for item in list1 if not any(
        metadata_matches(item, input2) for input2 in list2)] #, strict_mode)

    return missing_in_list1, missing_in_list2


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
        with open(error_file_name, "a", encoding='utf-8') as error_file:
            error_file.write(f"Error processing {file_path}: {e}\n")

    return metadata


def clear_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "w", encoding='utf-8') as file:
            file.write("")


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

                else:
                    with open(error_file_name, "a", encoding='utf-8') as error_file:
                        error_file.write(
                            f"Error processing {file_path}: Invalid audio file\n")

            else:
                with open(error_file_name, "a", encoding='utf-8') as error_file:
                    error_file.write(
                        f"Error processing {file_path}: File does not exist\n")

    return files_with_metadata


def scan_folder_for_audio_files(folder_path):
    audio_files = []

    for ext in ('*.mp3', '*.m4a', '*.flac', '*.wav', '*.ogg'):
        audio_files.extend(
            glob.glob(os.path.join(folder_path, ext), recursive=True))

    return audio_files


def process_input(input_path):
    if os.path.isfile(input_path) and (input_path.lower().endswith('.m3u8') or input_path.lower().endswith('.m3u')):
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        return extract_files_with_metadata(lines)

    elif os.path.isdir(input_path):
        audio_files = scan_folder_for_audio_files(input_path)
        files_with_metadata = []

        for file_path in audio_files:
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

            else:
                with open(error_file_name, "a", encoding='utf-8') as error_file:
                    error_file.write(
                        f"Error processing {file_path}: Invalid audio file\n")

        return files_with_metadata
    else:
        print(f"Error: Invalid input path: {input_path}")
        sys.exit(1)


def copy_possible_duplicates(duplicates, folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    for index, (item1, item2) in enumerate(duplicates, start=1):
        new_dir = os.path.join(folder_path, str(index))
        os.makedirs(new_dir, exist_ok=True)

        print(
            f"Copying '{item1['file_path']}' to '{os.path.join(new_dir, item1['file_name'])}'")
        print(
            f"Copying '{item2['file_path']}' to '{os.path.join(new_dir, item2['file_name'])}'")

        shutil.copy2(item1["file_path"], os.path.join(
            new_dir, item1["file_name"]))
        shutil.copy2(item2["file_path"], os.path.join(
            new_dir, item2["file_name"]))


if __name__ == "__main__":

    print("\nm3u-comparer v1.0.0\n")

    diff_file_name = "diff.txt"
    error_file_name = "errors.txt"
    match_file_name = "matches.txt"
    duplicate_folder_name = "duplicates"

    # strict_mode = False

    if os.path.exists("output.txt"):
        with open("output.txt", "r", encoding='utf-8') as output_files:
            for line in output_files:
                if line.startswith("diff_file_name"):
                    diff_file_name = line.split("=")[1].strip()
                elif line.startswith("error_file_name"):
                    error_file_name = line.split("=")[1].strip()
                elif line.startswith("match_file_name"):
                    match_file_name = line.split("=")[1].strip()
                elif line.startswith("duplicate_folder_name"):
                    duplicate_folder_name = line.split("=")[1].strip()
                # elif line.startswith("strict_mode"):
                #     strict_mode = line.split("=")[1].strip().lower() == "true"

    if not os.path.exists(diff_file_name) or not os.path.exists(error_file_name) or not os.path.exists(match_file_name) or not os.path.exists(duplicate_folder_name):
        print("Error: Invalid output file names")
        print("Please update or remove output.txt")
        sys.exit(1)

    clear_file(diff_file_name)
    clear_file(error_file_name)
    clear_file(match_file_name)

    if len(sys.argv) != 3:
        print("Error: Invalid number of arguments")
        print(
            "\n\nUsage: python3 comparer.py <m3u8-input1/folder1> <m3u8-input2/folder2>\n")
        print("\nExiting...")
        sys.exit(1)

    input1, input2 = sys.argv[1], sys.argv[2]

    print(
        f"Comparing inputs:\n\n          {input1} \n\n              and \n\n          {input2}")

    goodLines1_metadata = process_input(input1)
    goodLines2_metadata = process_input(input2)

    print(f"\n\nExtracted {len(goodLines1_metadata)} files from {input1}")
    print(f"Extracted {len(goodLines2_metadata)} files from {input2}\n")

    missing_in_input2, missing_in_input1 = compare_metadata_lists(
        goodLines1_metadata, goodLines2_metadata) #, strict_mode)

    matching_files = find_matching_files(
        goodLines1_metadata, goodLines2_metadata) #, strict_mode)

    if not missing_in_input1 and not missing_in_input2:
        print("No differences found!")
        sys.exit(0)

    print("\nDifferences found!\n")

    if os.path.exists(diff_file_name):
        with open(diff_file_name, "w", encoding='utf-8') as diff_file:
            diff_file.write("Differences found:\n\n")

            if len(missing_in_input1) > 0:
                diff_file.write(
                    f"    {len(missing_in_input1)} files not in {input1}:\n\n")
                for metadata in missing_in_input1:
                    diff_file.write(f"    {metadata['file_name']}\n")

            diff_file.write("\n")

            if len(missing_in_input2) > 0:
                diff_file.write(
                    f"    {len(missing_in_input2)} files not in {input2}:\n\n")
                for metadata in missing_in_input2:
                    diff_file.write(f"    {metadata['file_name']}\n")

        print(f"\nWrote results to {diff_file_name}")

    else:
        print(f"Error: Invalid output path: {diff_file_name}")
        sys.exit(1)

    if matching_files:
        with open(match_file_name, "w", encoding='utf-8') as match_file:
            match_file.write("Matches with different filenames:\n\n")
            for item1, item2 in matching_files:
                match_file.write(
                    f"{item1['file_name']} in {input1} matches {item2['file_name']} in {input2}\n")

                match_file.write(f"    {item1['file_name']} in {input1}:\n")
                match_file.write(f"        Title: {item1['title']}\n")
                match_file.write(f"        Artist: {item1['artist']}\n")
                match_file.write(f"        Album: {item1['album']}\n")
                match_file.write(
                    f"        Length: {round(item1['length'], 2)}\n")
                match_file.write(f"        Bitrate: {item1['bitrate']}\n\n")

                match_file.write(f"    {item2['file_name']} in {input2}:\n")
                match_file.write(f"        Title: {item2['title']}\n")
                match_file.write(f"        Artist: {item2['artist']}\n")
                match_file.write(f"        Album: {item2['album']}\n")
                match_file.write(
                    f"        Length: {round(item2['length'], 2)}\n")
                match_file.write(f"        Bitrate: {item2['bitrate']}\n\n")

        print(f"\nWrote possible duplicates to {match_file_name}")

        copy_duplicates = input(
            "\nCopy duplicates to new folders in the project directory? (y/n): ")

        if copy_duplicates.lower() == "y":
            print("\nCopying duplicates...")
            copy_possible_duplicates(matching_files, duplicate_folder_name)
            print("\nCopied duplicates to new folders in the project directory")

    if os.path.exists(error_file_name):
        with open(error_file_name, "r", encoding='utf-8') as error_file:
            if len(error_file.readlines()) > 0:
                print(f"\nErrors written to {error_file_name}")
