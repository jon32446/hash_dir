README
=========

The `hash_dir.py` script is a Python utility designed to compute the BLAKE2 hash of every file in a specified directory. One of its key features is its support for Unicode characters, which allows it to process files with names in various languages and symbols, including emojis.

The script works by recursively traversing the input directory and computing the hash for each file it encounters. The results, consisting of the file path and its corresponding hash, are then written to a UTF-8 encoded CSV file.

To ensure accuracy and reliability, the output of this script has been independently verified by comparing it against the output of the `b2sum` command-line utility, a widely used tool for computing and verifying BLAKE2 hashes. This makes `hash_dir.py` a reliable tool for checking the integrity of files in a directory.

BLAKE2 was chosen over MD5 or SHA for two reasons. Firstly, BLAKE2 is significantly faster than MD5, SHA-1, SHA-2, and SHA-3, making it a more efficient choice for hashing large amounts of data. Secondly, despite its speed, BLAKE2 is at least as secure as the latest standard SHA-3, providing a high level of security for the hashed data. This combination of speed and security makes BLAKE2 an excellent choice for file hashing.

**Usage**:

```
python hash_dir.py test
```

*Output has been independently verified by comparing against b2sum*:

```
find . -type f -exec b2sum "{}" \;
```
