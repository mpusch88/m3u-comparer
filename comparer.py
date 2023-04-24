#!/usr/bin/env python3

import os
import sys
import glob
import shutil
import urllib.parse
from tqdm import tqdm
from tinytag import TinyTag, TinyTagException


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

                # else:
                #     with open(errors_file_name, "a", encoding='utf-8') as error_file:
                #         error_file.write(
                #             f"Error processing {file_path}: Invalid audio file\n")

            else:
                with open(errors_file_name, "a", encoding='utf-8') as error_file:
                    error_file.write(
                        f"Error processing {file_path}: File does not exist\n")

    return files_with_metadata


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


def copy_possible_duplicates(duplicates, folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    for index, (item1, item2) in enumerate(duplicates, start=1):
        new_dir = os.path.join(folder_path, str(index))
        os.makedirs(new_dir, exist_ok=True)

        print(
            f"  Copying possible duplicate pair {index} to \\{new_dir}\\")

        shutil.copy2(item1["file_path"], os.path.join(
            new_dir, item1["file_name"]))
        shutil.copy2(item2["file_path"], os.path.join(
            new_dir, item2["file_name"]))


if __name__ == "__main__":

    print("\nm3u-comparer v1.0.0")

    diff_file_name = "diff.txt"
    errors_file_name = "errors.txt"
    similar_file_name = "similar.txt"
    matches_file_name = "matches.txt"
    duplicates_dir = "duplicates"

    strict_mode = False
    recursive1, recursive2 = False, False

    if os.path.exists("settings.txt"):
        with open("settings.txt", "r", encoding='utf-8') as output_files:
            for line in output_files:
                if line.startswith("diff_file_name"):
                    diff_file_name = line.split("=")[1].strip()
                elif line.startswith("errors_file_name"):
                    errors_file_name = line.split("=")[1].strip()
                elif line.startswith("similar_file_name"):
                    similar_file_name = line.split("=")[1].strip()
                elif line.startswith("matches_file_name"):
                    matches_file_name = line.split("=")[1].strip()
                elif line.startswith("duplicates_dir"):
                    duplicates_dir = line.split("=")[1].strip()
                elif line.startswith("strict_mode"):
                    strict_mode = line.split("=")[1].strip().lower() == "true"

    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("\nError: Invalid number of arguments")
        print("\nUsage:\n\n  python3 comparer.py <m3u8-input1/folder1> <m3u8-input2/folder2>\n  python3 comparer.py <m3u8-input1/folder1>")
        print("\nExiting...")
        sys.exit(1)

    input1 = sys.argv[1]
    input2 = sys.argv[2] if len(sys.argv) == 3 else input1

    print(f"    Strict mode: {strict_mode}\n")

    if os.path.isdir(input1):
        recursive1 = input(
            f"Scan {input1} recursively? ('Y' or 'y')   ").lower() == "y"

    if os.path.isdir(input2):
        recursive2 = input(
            f"Scan {input2} recursively? ('Y' or 'y')   ").lower() == "y"

    clear_file(diff_file_name)
    clear_file(errors_file_name)
    clear_file(matches_file_name)
    clear_file(similar_file_name)

    print(
        f"\n\nComparing inputs:\n\n          {input1} \n\n              and \n\n          {input2}\n")

    print()
    goodLines1_metadata = process_input(input1, recursive1)
    print()
    goodLines2_metadata = process_input(input2, recursive2)

    print(f"\n\nExtracted {len(goodLines1_metadata)} files from {input1}")
    print(f"Extracted {len(goodLines2_metadata)} files from {input2}\n\n")

    missing_in_input2, missing_in_input1 = compare_metadata_lists(
        goodLines1_metadata, goodLines2_metadata, strict_mode)

    matching_files, similar_files = find_matching_and_similar_files(
        goodLines1_metadata, goodLines2_metadata, strict_mode)

    if not missing_in_input1 and not missing_in_input2:
        print("\n\nNo differences found!\n")
    else:
        print("\n\nDifferences found!\n")

        with open(diff_file_name, "w", encoding='utf-8') as diff_file:
            diff_file.write(
                f"Differences found: {len(missing_in_input1 + missing_in_input2)}\n\n")

            if len(missing_in_input1) > 0:
                diff_file.write(
                    f"    {len(missing_in_input1)} files not in {input1}:\n\n")
                for metadata in missing_in_input1:
                    diff_file.write(f"      {metadata['file_name']}\n")

            diff_file.write("\n")

            if len(missing_in_input2) > 0:
                diff_file.write(
                    f"    {len(missing_in_input2)} files not in {input2}:\n\n")
                for metadata in missing_in_input2:
                    diff_file.write(f"      {metadata['file_name']}\n")

        print(f"\nWrote results to {diff_file_name}")

    if matching_files:
        with open(matches_file_name, "w", encoding='utf-8') as match_file:
            match_file.write(f"Exact matches: {len(matching_files)}\n\n")
            for item1, item2 in matching_files:
                match_file.write(f"  {item1['file_name']}  --  {input1}\n")
                match_file.write(f"  {item2['file_name']}  --  {input2}\n\n")

        print(f"\nWrote exact matches to {matches_file_name}")

    if similar_files:
        with open(similar_file_name, "w", encoding='utf-8') as similar_file:
            similar_count_line = f"Potential duplicates: {len(similar_files)}\n\n"
            similar_file.write(similar_count_line)
            for item1, item2 in similar_files:
                similar_file.write(
                    f"{item1['file_name']} in {input1} matches {item2['file_name']} in {input2}\n")

                similar_file.write(f"    {item1['file_name']} in {input1}:\n")
                similar_file.write(f"        Title: {item1['title']}\n")
                similar_file.write(f"        Artist: {item1['artist']}\n")
                similar_file.write(f"        Album: {item1['album']}\n")
                similar_file.write(
                    f"        Length: {round(item1['length'], 2)}\n")
                similar_file.write(f"        Bitrate: {item1['bitrate']}\n\n")

                similar_file.write(f"    {item2['file_name']} in {input2}:\n")
                similar_file.write(f"        Title: {item2['title']}\n")
                similar_file.write(f"        Artist: {item2['artist']}\n")
                similar_file.write(f"        Album: {item2['album']}\n")
                similar_file.write(
                    f"        Length: {round(item2['length'], 2)}\n")
                similar_file.write(f"        Bitrate: {item2['bitrate']}\n\n")

        print(f"\nWrote possible duplicates to {similar_file_name}")

        copy_duplicates = input(
            "\n\nCopy possible duplicates to new folders in the project directory? (y/n): ")

        if copy_duplicates.lower() == "y":
            print("\nCopying possible duplicates...\n")
            copy_possible_duplicates(similar_files, duplicates_dir)
            print("\nCopied possible duplicates to new folders in the project directory")

    if os.path.exists(errors_file_name):
        with open(errors_file_name, "r", encoding='utf-8') as error_file:
            if len(error_file.readlines()) > 0:
                print(f"\n\nErrors written to {errors_file_name}")
