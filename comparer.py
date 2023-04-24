#!/usr/bin/env python3

import os
import sys
from settings import diff_file_name, errors_file_name, similar_file_name, matches_file_name, duplicates_dir, strict_mode
from utils import clear_file, copy_possible_duplicates
from file_processing import process_input, compare_metadata_lists, find_matching_and_similar_files


if __name__ == "__main__":
    print("\n********** m3u-comparer v1.0.0 **********")

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("\nError: Invalid number of arguments")
        print(
            "\nUsage:\n\n  python3 comparer.py <m3u8-input1/folder1> [<m3u8-input2/folder2>]\n")
        print("\nExiting...")
        sys.exit(1)

    input1 = sys.argv[1]
    input2 = sys.argv[2] if len(sys.argv) == 3 else input1

    print(f"\nStrict mode: {strict_mode}")
    print(f"\nComparing inputs:\n")
    print(f"    {input1}")
    print(f"    {input2}\n")

    recursive1, recursive2 = False, False

    if os.path.isdir(input1):
        recursive1 = input(
            f"Scan {input1} recursively? ('Y' or 'y')   ").lower() == "y"

        if len(sys.argv) == 2:
            recursive2 = recursive1

        elif len(sys.argv) == 3 and os.path.isdir(input2):
            recursive2 = input(
                f"Scan {input2} recursively? ('Y' or 'y')   ").lower() == "y"

    clear_file(diff_file_name)
    clear_file(errors_file_name)
    clear_file(matches_file_name)
    clear_file(similar_file_name)
    print()

    goodLines1_metadata = process_input(input1, recursive1)

    if input1 != input2:
        print()
        goodLines2_metadata = process_input(input2, recursive2)
    else:
        goodLines2_metadata = goodLines1_metadata

    if goodLines1_metadata == [] and goodLines2_metadata == []:
        print("\n  No files found in either input!")
        print("\nExiting...")
        sys.exit(1)

    if goodLines1_metadata == []:
        goodLines1_metadata = goodLines2_metadata

    elif goodLines2_metadata == []:
        goodLines2_metadata = goodLines1_metadata

    if input1 != input2:
        print(f"\n  Found {len(goodLines1_metadata)} files in {input1}")
        print(f"  Found {len(goodLines2_metadata)} files in {input2}\n")
    else:
        print(f"\n  Found {len(goodLines1_metadata)} files in {input1}\n")

    matching_files, similar_files = find_matching_and_similar_files(
        goodLines1_metadata, goodLines2_metadata, strict_mode)

    print()

    missing_in_input2, missing_in_input1 = compare_metadata_lists(
        goodLines1_metadata, goodLines2_metadata, strict_mode, matching_files)

    if not missing_in_input1 and not missing_in_input2:
        print("\n  No differences between inputs found!")
    else:
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

        print(f"\n  Wrote input list differences to {diff_file_name}")

    if not matching_files:
        print("  No exact matches found!")
    else:
        with open(matches_file_name, "w", encoding='utf-8') as match_file:
            match_file.write(f"Exact matches: {len(matching_files)}\n\n")
            for item1, item2 in matching_files:
                match_file.write(f"  {item1['file_name']}  --  {input1}\n")
                match_file.write(f"  {item2['file_name']}  --  {input2}\n\n")

        print(f"  Wrote exact matches to {matches_file_name}")

    if not similar_files:
        print("  No potential duplicates found!")
    else:
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

        print(f"  Wrote possible duplicates to {similar_file_name}")

        copy_duplicates = input(
            "\nCopy possible duplicates to new folders in the project directory? (y/n): ")

        if copy_duplicates.lower() == "y":
            print("")
            copy_possible_duplicates(similar_files, duplicates_dir)

    if os.path.exists(errors_file_name):
        with open(errors_file_name, "r", encoding='utf-8') as error_file:
            if len(error_file.readlines()) > 0:
                print(f"\nErrors written to {errors_file_name}")

    print("\nExiting...")
