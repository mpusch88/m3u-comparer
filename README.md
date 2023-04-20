# m3u-comparer (v1.0.0)

m3u-comparer is a python script that compares two m3u / m3u8 playlists and outputs the differences. Only the files are considered in the comparison, not the paths.

## How to Use

### Prerequisites

1. Two m3u / m3u8 playlists to compare.
2. Python 3.6 or higher.

### Building the Project

1. Clone the repository or download the project files:

```bash
git clone https://www.github.com/mpusch88/m3u-comparer
```

### Running the Program

1. Navigate to the project directory.
2. Run 'python m3u-comparer.py' to run the script.
3. When prompted, enter the path of the first playlist.
4. When prompted, enter the path of the second playlist.
5. The script will output the differences between the two playlists.

## Context

This project uses a modified version of  <https://github.com/mpoon/gpt-repository-loader> to maintain up to date code context for use with ChatGPT / GPT4.

Example command:

```bash
python gpt_repository_loader.py ../m3u-comparer -p ../m3u-comparer/.preamble -o ../m3u-comparer/context.txt -t 4000 -m 10
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
