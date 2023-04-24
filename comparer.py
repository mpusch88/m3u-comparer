#!/usr/bin/env python3

import os
import sys
from settings import diff_file_name, errors_file_name, similar_file_name, matches_file_name, duplicates_dir, strict_mode
from utils import clear_file, copy_possible_duplicates
from file_processing import process_input, compare_metadata_lists, find_matching_and_similar_files


if __name__ == "__main__":
    print("\nm3u-comparer v1.0.0")

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("\nError: Invalid number of arguments")
        print(
            "\nUsage:\n\n  python3 comparer.py <m3u8-input1/folder1> [<m3u8-input2/folder2>]\n")
        print("\nExiting...")
        sys.exit(1)

    input1 = sys.argv[1]
    input2 = sys.argv[2] if len(sys.argv) == 3 else input1

    print(f"    Strict mode: {strict_mode}\n")

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
