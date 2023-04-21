#!/usr/bin/env python3

import os
import sys
import glob
import urllib.parse
from tinytag import TinyTag, TinyTagException


def compare_metadata_lists(list1, list2):
    def metadata_matches(item1, item2):
        return (item1["title"] == item2["title"]
                and item1["artist"] == item2["artist"]
                and item1["album"] == item2["album"]
                and round(item1["length"]) == round(item2["length"]))

    missing_in_list1 = [item for item in list2 if not any(
        metadata_matches(item, input1) for input1 in list1)]
    missing_in_list2 = [item for item in list1 if not any(
        metadata_matches(item, input2) for input2 in list2)]

    return missing_in_list1, missing_in_list2


def extract_audio_metadata(file_path):
    metadata = {}

    try:
        audio = TinyTag.get(file_path)
        metadata["title"] = audio.title if audio.title else "Unknown"
        metadata["artist"] = audio.artist if audio.artist else "Unknown"
        metadata["album"] = audio.album if audio.album else "Unknown"
        metadata["length"] = audio.duration if audio.duration else 0
    except TinyTagException as e:
        with open("errors.txt", "a", encoding='utf-8') as error_file:
            error_file.write(f"Error processing {file_path}: {e}\n")
    return metadata


def clear_errors_file():
    if os.path.exists("errors.txt"):
        with open("errors.txt", "w", encoding='utf-8') as error_file:
            error_file.write("")


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
                if metadata:  # Check if metadata is not empty
                    file_data = {
                        "file_name": os.path.basename(file_path),
                        "title": metadata.get("title"),
                        "artist": metadata.get("artist"),
                        "album": metadata.get("album"),
                        "length": metadata.get("length")
                    }

                    files_with_metadata.append(file_data)
                else:
                    with open("errors.txt", "a", encoding='utf-8') as error_file:
                        error_file.write(
                            f"Error processing {file_path}: Invalid audio file\n")
            else:
                with open("errors.txt", "a", encoding='utf-8') as error_file:
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
        return [extract_audio_metadata(file_path) for file_path in audio_files]
    else:
        print(f"Error: Invalid input path: {input_path}")
        sys.exit(1)


if __name__ == "__main__":
    print("\nm3u-comparer v1.0.0\n")

    if len(sys.argv) != 3:
        print("Error: Invalid number of arguments")
        print(
            "\n\nUsage: python3 comparer.py <m3u8-input1/folder1> <m3u8-input2/folder2>\n")
        print("\nExiting...")
        sys.exit(1)

    input1, input2 = sys.argv[1], sys.argv[2]

    print(
        f"Comparing inputs:\n\n          {input1} \n\n              and \n\n          {input2}")

    clear_errors_file()

    goodLines1_metadata = process_input(input1)
    goodLines2_metadata = process_input(input2)

    print(f"\n\nExtracted {len(goodLines1_metadata)} files from {input1}")
    print(f"Extracted {len(goodLines2_metadata)} files from {input2}\n")

    missing_in_input2, missing_in_input1 = compare_metadata_lists(
        goodLines1_metadata, goodLines2_metadata)

    if not missing_in_input1 and not missing_in_input2:
        print("No differences found!")
        sys.exit(0)

    print("\nDifferences found!\n")

    with open("differences.txt", "w", encoding='utf-8') as diff_file:
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

    print("\nWrote results to differences.txt")

    if os.path.exists("errors.txt"):
        with open("errors.txt", "r", encoding='utf-8') as error_file:
            if len(error_file.readlines()) > 0:
                print("\nErrors written to errors.txt")
