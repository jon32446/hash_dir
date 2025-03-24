#!/usr/bin/env python3
"""
hash_dir.py - Compute BLAKE2 hashes for all files in a directory

This script recursively traverses a directory and computes BLAKE2 hashes for all files
it encounters, supporting Unicode filenames including international characters and emojis.
Results are written to a CSV file or stdout.
"""

import os
import hashlib
import csv
import sys
import argparse
import multiprocessing
from typing import Tuple, Optional
import logging
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def hash_file(filename: str) -> Tuple[Optional[str], int]:
    """
    Compute the BLAKE2 hash of a file.
    
    Args:
        filename: Path to the file to hash
        
    Returns:
        Tuple of (hash_digest, file_size) where hash_digest is None if an error occurred
    """
    try:
        h = hashlib.blake2b()
        # Determine optimal buffer size (4KB to 8MB depending on file size)
        file_size = os.path.getsize(filename)
        buffer_size = min(max(4096, file_size // 1000), 8 * 1024 * 1024)
        
        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(buffer_size)
                if not chunk:
                    break
                h.update(chunk)
        return (h.hexdigest(), file_size)
    except (IOError, PermissionError, OSError) as e:
        logger.error(f"Error processing {filename}: {str(e)}")
        return (None, 0)

def worker(file_info: Tuple[int, str]) -> Tuple[int, str, Optional[str], int]:
    """
    Worker function for parallel processing.
    
    Args:
        file_info: Tuple containing (original_index, file_path)
        
    Returns:
        Tuple of (original_index, file_path, hash, file_size) where hash is None if an error occurred
    """
    original_index, file_path = file_info
    hash_result, file_size = hash_file(file_path)
    return (original_index, file_path, hash_result, file_size)

def format_size(bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        bytes: Size in bytes
        
    Returns:
        Human-readable string (e.g., "4.2 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"

def hash_directory(directory: str, output_file: str, num_workers: int = None) -> None:
    """
    Hash all files in a directory recursively and write results to a CSV file or stdout.
    
    Args:
        directory: Directory to process
        output_file: Path to output CSV file or "-" for stdout
        num_workers: Number of worker processes (defaults to CPU count)
    """
    start_time = time.time()
    if not num_workers:
        num_workers = min(32, multiprocessing.cpu_count())
    logger.info(f"Using {num_workers} worker processes")
    
    # Get list of all files first, preserving the order from os.walk
    file_list = []
    total_size = 0
    # Convert to absolute path for consistent processing
    abs_directory = os.path.abspath(directory)
    logger.info(f"Scanning directory: {directory}")
    for root, dirs, files in os.walk(directory):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                file_size = os.path.getsize(file_path)
                total_size += file_size
                # Store the index with the file path to preserve original order
                file_list.append((len(file_list), file_path))
            except (OSError, PermissionError) as e:
                logger.warning(f"Cannot access {file_path}: {str(e)}")
    
    total_files = len(file_list)
    logger.info(f"Found {total_files} files to process ({format_size(total_size)})")
    
    # Process files in parallel with a progress bar
    results = []
    processed_bytes = 0
    
    # Create a progress bar that tracks bytes instead of files
    with tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        desc="Hashing files"
    ) as pbar:
        with multiprocessing.Pool(processes=num_workers) as pool:
            for original_index, file_path, file_hash, file_size in pool.imap_unordered(worker, file_list):
                results.append((original_index, file_path, file_hash, file_size))
                processed_bytes += file_size
                pbar.update(file_size)
    
    # Sort results by original index to preserve os.walk order
    results.sort(key=lambda x: x[0])
    
    # Write results to CSV (file or stdout)
    successful_files = 0
    
    # Function to make paths relative to the input directory
    def make_path_relative(path):
        # Use os.path.relpath to get the path relative to the input directory
        rel_path = os.path.relpath(path, directory)
        # Convert backslashes to forward slashes for consistency across platforms
        return rel_path.replace('\\', '/')
    
    # Determine if we're writing to stdout or a file
    if output_file == "-":
        # Write to stdout
        # For Windows compatibility, explicitly set newline handling
        if sys.platform == 'win32':
            writer = csv.writer(sys.stdout, lineterminator='\n')
        else:
            writer = csv.writer(sys.stdout)
        writer.writerow(["File Path", "BLAKE2 Hash"])
        for _, file_path, file_hash, _ in results:
            if file_hash:
                writer.writerow([make_path_relative(file_path), file_hash])
                successful_files += 1
        output_message = "standard output"
    else:
        # Write to file
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["File Path", "BLAKE2 Hash"])
            for _, file_path, file_hash, _ in results:
                if file_hash:
                    writer.writerow([make_path_relative(file_path), file_hash])
                    successful_files += 1
        output_message = f"file {output_file}"
    
    elapsed_time = time.time() - start_time
    throughput = processed_bytes / elapsed_time if elapsed_time > 0 else 0
    
    logger.info(f"Completed hashing {successful_files}/{total_files} files ({format_size(processed_bytes)}) in {elapsed_time:.2f} seconds")
    logger.info(f"Average throughput: {format_size(throughput)}/s")
    logger.info(f"Results written to {output_message}")

def main() -> None:
    """Parse arguments and execute the script."""
    parser = argparse.ArgumentParser(
        description='Compute BLAKE2 hashes of all files in a directory recursively.'
    )
    parser.add_argument(
        'directory',
        help='Directory to hash'
    )
    parser.add_argument(
        '-o', '--output',
        default='dir_hashes_blake2.csv',
        help='Output CSV file (default: dir_hashes_blake2.csv). Use "-" for stdout'
    )
    parser.add_argument(
        '-w', '--workers',
        type=int,
        help='Number of worker processes (default: number of CPU cores)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    if not os.path.isdir(args.directory):
        logger.error(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    try:
        hash_directory(args.directory, args.output, args.workers)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
