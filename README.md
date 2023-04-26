# m3u-comparer (WIP)

![GitHub license](https://img.shields.io/github/license/mpusch88/m3u-comparer)

A Python script for comparing m3u/m3u8 playlists or directories containing audio files based on metadata, and finding duplicates or potential duplicates.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Output](#output)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [Context](#context)
- [License](#license)

## Overview

m3u-comparer is a powerful and versatile tool for managing and organizing audio file collections. It can compare two playlists or directories, and search a single playlist or directory for duplicates or potential duplicates. By analyzing metadata such as artist, title, album, length, and bitrate, m3u-comparer can detect matching or similar files, even if they have different names.

## Requirements

- Python 3.6 or higher
- Python packages: tinytag, tqdm, keyboard

## Installation

1. Install the required packages (elevated privileges may be required):

   ```bash
   pip install -r requirements.txt
   ```

2. Clone the repository or download the project files:

   ```bash
   git clone https://www.github.com/mpusch88/m3u-comparer
   ```

## Usage

- Compare two m3u/m3u8 playlists or directories:

   ```bash
   python comparer.py /path/to/input1 /path/to/input2
   ```

- Search a single directory for duplicates or potential duplicates:

   ```bash
   python comparer.py /path/to/m3u8-input1
   ```

The script will prompt for additional options like searching directories recursively or copying potential duplicates.

## Output

The program generates the following output files:

1. diff.txt: Differences between the two inputs.
2. similar.txt: Potential duplicates with matching metadata but different names.
3. matches.txt: Exact duplicates with matching metadata and names.
4. errors.txt: Errors encountered during processing.
5. 'duplicates' folder: optional output folder that holds subfolders containing possible duplicates.

**Warning: Output files are overwritten each time the program is run. If the user chooses to copy potential duplicates, the target duplicates folder will be emptied.**

## Configuration

Use the settings.py file to configure the script's behavior. You can set variables for output file names, output directory names, and strict mode (which forces the script to only consider files with exactly matching metadata as possible duplicates).

## Contributing

Contributions are welcome! Please fork the repository, create a new branch for your feature or bugfix, commit your changes with clear and concise messages, and open a pull request with a detailed description of your changes.

## Context

This project uses a modified version of  <https://github.com/mpoon/gpt-repository-loader> to maintain up to date code context for use with ChatGPT / GPT4.

To use the context loader, clone the following repository into the same folder containig your m3u-comparer repository:

```bash
git clone https://github.com/mpusch88/gpt-repository-loader
```

Then, navigate to the gpt-repository-loader folder and run the gpt_repository_loader.py script with the following arguments:

```bash
python gpt_repository_loader.py ../m3u-comparer -p ../m3u-comparer/.preamble -o ../m3u-comparer/context/context.txt -t 4000 -m 10
```

*Note: if you don't have access to GPT 4, using -t 2000 is recommended.*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
