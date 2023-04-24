# m3u-comparer (WIP)

![GitHub license](https://img.shields.io/github/license/mpusch88/m3u-comparer)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Program](#running-the-program)
- [Program Output](#program-output)
- [Program Settings](#program-settings)
- [Contributing](#contributing)
- [Context](#context)
- [License](#license)

## Overview

m3u-comparer is a Python script designed to compare two m3u or m3u8 playlists, or directories containing audio files, by focusing on metadata while disregarding file paths. The script can also search through directories recursively if needed. By analyzing metadata attributes such as artist, title, album, length, and bitrate, the tool effectively identifies differences between audio files and detects files with matching metadata but different names.

Additionally, m3u-comparer can be used to search a single playlist or folder for duplicates or potential duplicates, enhancing its versatility for managing audio files. Ideal for individuals with extensive audio file collections, m3u-comparer works well in combination with tools like OneTagger to streamline the process of organizing and cleaning up a music library. The script simplifies the task of comparing playlist contents, locating possible duplicates, and identifying potential duplicates, providing a powerful solution for assessing and organizing audio file collections.

## Features

- Compare two m3u/m3u8 playlists or directories containing audio files
- Search a single directory for duplicates or potential duplicates
- Identify differences in metadata (artist, title, album, length, and bitrate)
- Detect potential duplicates that have matching metadata but different file names
- Detect duplicate files with matching metadata and file names
- Generate detailed output files (playlist differences, possible duplicates, exact matches, and errors)
- Optionally copy potential duplicates to new directories for easy comparison
- Manually set output file names, directories, and strict mode in settings.py

## Requirements

- Python 3.6 or higher
- tinytag Python package (Used for reading file metadata)
- tqdm Python package (Used for progress bars)

## Installation

1. Install the required packages:

   ```bash
   pip install tinytag tqdm
   ```

2. Clone the repository or download the project files:

   ```bash
   git clone https://www.github.com/mpusch88/m3u-comparer
   ```

### Running the Program

1. Navigate to the project directory.
2. Run the comparer.py script with one or two arguments - both being paths to m3u/m3u8 playlists or directories containing audio files.
   - If one input is provided, the script will only search for matches and potential duplicates.
   - If two inputs are provided, the script will compare the two inputs.
3. If a directory is selected as input, the user will be prompted to select whether to search the directory recursively.
4. If possible duplicates are found, the script will prompt to copy the matching files to new directories created in a project subfolder called "duplicates" by default.
5. By default, the script will output any differences between the two inputs in diff.txt, any possible duplicates in similar.txt, any exact matches in matches.txt, and any errors in errors.txt.

Example usage:

```bash
python comparer.py /path/to/m3u8-input1 /path/to/m3u8-input2
```

### Program Output

The program will output the following files:

1. diff.txt: a list of differences between the two inputs.
2. similar.txt: a list of files that have the same metadata but different names.
3. matches.txt: a list of files that have the same metadata and names.
4. errors.txt: a list of errors encountered while processing the inputs.
5. 'duplicates' folder: a folder composed of subfolders that contain possible duplicates.


<b>Warning: Output files are overwritten each time the program is run. If user selects to copy potential duplicates, target duplicates directory will be cleared.</b>


### Program Settings

The program can be configured using the settings.py file. The file contains the following variables:

- strict_mode: a boolean value that determines whether the program is in strict mode or not. In strict mode, the program increases the strictness of the metadata comparison, requiring that all metadata attributes match exactly for files to be considered possible duplicates. By default, the program is not in strict mode.
- diff_file_name: stores differences between the two inputs. By default, the file is called "diff.txt".
- similar_file_name: stores possible duplicates. By default, the file is called "similar.txt".
- matches_file_name: stores exact matches. By default, the file is called "matches.txt".
- errors_file_name: stores errors. By default, the file is called "errors.txt".
- duplicates_dir: the name of the directory that will be created to store the possible duplicates. By default, the directory is called "duplicates".

## Contributing

Contributions to this project are welcomed! If you'd like to contribute, please follow these guidelines:

1. Fork the repository.
2. Create a new branch with a descriptive name for your feature or bugfix.
3. Commit your changes to the new branch, and make sure to write clear and concise commit messages.
4. Open a pull request, and provide a detailed description of your changes.

Please ensure that your code follows the project's coding style and conventions, and make sure to update any relevant documentation if necessary.

## Context

This project uses a modified version of  <https://github.com/mpoon/gpt-repository-loader> to maintain up to date code context for use with ChatGPT / GPT4.

To use the context loader, clone the following repository into the same folder containig your m3u-comparer repository:

```bash
git clone https://github.com/mpusch88/gpt-repository-loader
```

Then, navigate to the gpt-repository-loader folder and run the gpt_repository_loader.py script with the following arguments:

```bash
python gpt_repository_loader.py ../m3u-comparer -p ../m3u-comparer/.preamble -o ../m3u-comparer/context.txt -t 4000 -m 10
```

*Note: if you don't have access to GPT 4, using -t 2000 is recommended.*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
