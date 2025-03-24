# hash_dir

A high-performance Python utility to compute BLAKE2 hashes for all files in a directory with parallel processing.

## Overview

The `hash_dir.py` script recursively traverses a directory and computes BLAKE2 hashes for all files it encounters. It features:

- **Parallel processing**: Utilizes all available CPU cores for maximum performance
- **Progress tracking**: Real-time progress display showing bytes processed per second
- **Unicode support**: Handles files with names in various languages and symbols, including emojis
- **Robust error handling**: Gracefully handles permission errors and other issues
- **Human-readable output**: Displays file sizes and processing speeds in appropriate units (KB, MB, GB)

Results are written to a UTF-8 encoded CSV file with file paths and their corresponding hashes.

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
python hash_dir.py directory_to_hash
```

### Advanced Options

```bash
# Specify custom output file
python hash_dir.py directory_to_hash -o custom_output.csv

# Set specific number of worker processes (default: number of CPU cores, up to a maximum of 32)
python hash_dir.py directory_to_hash -w 4

# Enable verbose logging
python hash_dir.py directory_to_hash -v

# Get help
python hash_dir.py --help
```

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `directory` | Directory to hash (required) |
| `-o, --output` | Output CSV file (default: dir_hashes_blake2.csv) |
| `-w, --workers` | Number of worker processes (default: number of CPU cores, up to a maximum of 32) |
| `-v, --verbose` | Enable verbose logging |

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
