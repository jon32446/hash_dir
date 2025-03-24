# hash_dir

A high-performance Python utility to compute BLAKE2 hashes for all files in a directory with parallel processing.

## Overview

The `hash_dir.py` script recursively traverses a directory and computes BLAKE2 hashes for all files it encounters. It features:

- **Parallel processing**: Utilizes all available CPU cores for maximum performance
- **Progress tracking**: Real-time progress display showing bytes processed per second
- **Unicode support**: Handles files with names in various languages and symbols, including emojis
- **Robust error handling**: Gracefully handles permission errors and other issues
- **Human-readable output**: Displays file sizes and processing speeds in appropriate units (KB, MB, GB)
- **Natural ordering**: Preserves the natural ordering of files as encountered by os.walk
- **Flexible output**: Can write to a file (default and recommended) or to stdout

Results are written to a UTF-8 encoded CSV file with file paths and their corresponding hashes by default.

## Why BLAKE2?

BLAKE2 was chosen over MD5 or SHA for two primary reasons:

1. **Performance**: BLAKE2 is significantly faster than MD5, SHA-1, SHA-2, and SHA-3, making it ideal for hashing large amounts of data.
2. **Data Integrity**: Despite its speed, BLAKE2 offers excellent collision resistance comparable to SHA-3, making it highly reliable for detecting even the smallest file modifications.

The output of this script has been independently verified by comparing it against the output of the `b2sum` command-line utility.

## Installation

```bash
# Clone the repository
git clone REPO_URL
cd hash_dir

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python hash_dir.py /path/to/directory
```

This will hash all files in the specified directory and its subdirectories, writing results to `dir_hashes_blake2.csv` in the current directory.

### Custom Output File

```bash
python hash_dir.py /path/to/directory -o custom_output.csv
```

### Output to stdout

```bash
python hash_dir.py /path/to/directory -o -
```

**Note:** Writing to a file (the default) is preferred over stdout because it ensures proper UTF-8 encoding for filenames with international characters or emojis. When redirecting stdout to a file, the encoding depends on your terminal settings, which may not properly handle Unicode characters.

### Control Worker Processes

```bash
python hash_dir.py /path/to/directory -w 8
```

This limits the hash operation to 8 worker processes instead of using all available CPU cores.

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `directory` | Directory to hash (required) |
| `-o, --output` | Output CSV file (default: dir_hashes_blake2.csv). Use "-" for stdout |
| `-w, --workers` | Number of worker processes (default: number of CPU cores, up to a maximum of 32) |
| `-v, --verbose` | Enable verbose logging |

### Full Options

```
usage: hash_dir.py [-h] [-o OUTPUT] [-w WORKERS] [-v] directory

Compute BLAKE2 hashes of all files in a directory recursively.

positional arguments:
  directory             Directory to hash

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output CSV file (default: dir_hashes_blake2.csv). Use "-" for stdout
  -w WORKERS, --workers WORKERS
                        Number of worker processes (default: number of CPU cores)
  -v, --verbose         Enable verbose logging
```

## Output Format

The output CSV file contains two columns:

1. **File Path**: Relative path to the file from the specified directory
2. **BLAKE2 Hash**: Hexadecimal representation of the BLAKE2 hash

Example:
```
File Path,BLAKE2 Hash
docs/example.txt,7d5164b96e93e46735f724292e1b13aac77f1d9dbdb80d5c3682d2a1a57d6a1e596dff1e148106ec9bff4aea522865eda5dd0a96b224edaf7a49c701e82e10da
images/logo.png,b78dae85d609f63f0e925560a5c3506f2d4ae63b03266d1b99616e488d8e73fa6193aa4a5e78c39526a44d92bd554c01f79bfc3bd9b638caf8c25ef7d3dc7a8d
```

## Performance Considerations

### SSD vs HDD Performance

- **With SSDs**: The process is typically CPU-bound. More worker processes generally improve performance until you reach your CPU core count.
- **With HDDs**: The process is typically I/O bound. Adding more workers beyond 1 may not improve performance and could potentially cause thrashing.

### Optimizing Worker Count

The default worker count is set to `min(32, CPU_count)`, which works well for SSD-based systems. However:

- If you're running on an HDD, try reducing the worker count to 1 using the `-w` option
- If you're running on a high-core-count server with SSDs, the default should work well
- Monitor system resource usage to identify bottlenecks:
  - High CPU usage across cores suggests you're CPU-bound
  - Low CPU usage with high disk activity suggests you're I/O bound

Experiment with different worker counts to find the optimal performance for your specific hardware.

On a modern multi-core system with SSD storage, `hash_dir.py` can process files at rates exceeding 300 MB/s, with the exact speed depending on storage devices and CPU capability.

## Example Output

```
Using 8 worker processes
Scanning directory: /path/to/dir
Found 1000 files to process (2.45 GB)
Hashing files: 100%|████████████████| 2.45G/2.45G [00:30<00:00, 85.3MB/s]
Completed hashing 998/1000 files (2.45 GB) in 30.12 seconds
Average throughput: 85.32 MB/s
Results written to dir_hashes_blake2.csv
```

## Verification

Results can be independently verified using the `b2sum` command-line utility:

```bash
find . -type f -exec b2sum "{}" \;
```
