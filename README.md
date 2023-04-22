# m3u-comparer (v1.0.0)

m3u-comparer is a Python script designed to compare two m3u / m3u8 playlists or directories containing audio files, highlighting differences in metadata while disregarding file paths. By evaluating metadata attributes like artist, title, album, length, and bitrate, this tool effectively identifies disparities between two sets of audio files, while also detecting files that contain the same metadata but different file names.

m3u-comparer streamlines the process of comparing playlist contents and locating possible duplicates, offering a powerful solution for assessing and organizing audio file collections.

## How to Use

### Prerequisites

1. Two m3u / m3u8 playlists or directories containing audio files to compare.
2. Python 3.6 or higher.
3. `tinytag` Python package: a library used to extract audio metadata like title, artist, album, length, and bitrate. Needed to get metadata from audio files. Install it using the following command:

```bash
pip install tinytag
```

### Building the Project

1. Clone the repository or download the project files:

```bash
git clone https://www.github.com/mpusch88/m3u-comparer
```

### Running the Program

1. Navigate to the project directory.
2. Run the comparer.py script with two arguments: the first is the path to the first m3u/m3u8 playlist or directory, and the second is the path to the second m3u/m3u8 playlist or directory.
3. If possible duplicates are found, the script will ask prompt to copy the matching files to new directories in the project folder.
4. By default, the script will output any differences between the two inputs in diff.txt, any possible duplicates in matches.txt, and any errors in errors.txt. You can configure the output file names in the output.txt file.

Example usage:

```bash
python comparer.py <m3u8-input1/folder1> <m3u8-input2/folder2>
```

### Program Output

The program will output the following files:

1. diff.txt: a list of differences between the two inputs.
2. matches.txt: a list of files that have different names but the same metadata.
3. errors.txt: a list of errors encountered while processing the inputs.

## Context

This project uses a modified version of  <https://github.com/mpoon/gpt-repository-loader> to maintain up to date code context for use with ChatGPT / GPT4.

Example command:

```bash
python gpt_repository_loader.py ../m3u-comparer -p ../m3u-comparer/.preamble -o ../m3u-comparer/context.txt -t 4000 -m 10
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
