# Crypt Hash Cracker Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Hash Processing](#hash-processing)
5. [Examples](#examples)

## Project Overview📝
The Crypt Hash Cracker is a command-line tool designed to crack various types of cryptographic hashes using a dictionary-based approach. The project consists of two main components: a hash generation tool (`hash_create.py`) for creating test data, and the main cracking tool (`hash.py`). It supports multiple hash types including MD5, SHA1, SHA256, SHA384, and SHA512, making it versatile for testing and educational purposes.

## Installation⚙️
To install and run the Crypt Hash Cracker locally, follow these steps:

1. Clone the project repository:
```bash
git clone https://github.com/RobCyberLab/Crypt-Hash-Cracker.git
```

2. Navigate to the project directory:
```bash
cd crypt-hash-cracker
```

3. Install required Python packages:
```bash
pip install requests urllib3 tqdm
```

4. Download a wordlist (e.g., rockyou.txt) for testing:
```bash
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
```

## Usage📖
The project consists of two main scripts:

### Hash Creation (hash_create.py)
1. Place your wordlist file (e.g., rockyou.txt) in the project directory
2. Run the hash creation script:
```bash
python3 hash_create.py
```
- The script will generate `all_hashes.txt` containing hashes for each password in various formats

### Hash Cracking (hash.py)
The main cracking tool supports several modes of operation:

1. Crack a single hash:
```bash
python3 hash.py -s <hash>
```

2. Crack multiple hashes from a file:
```bash
python3 hash.py -f <hashfile>
```

3. Additional options:
   - `-t, --threads`: Number of threads (default: 4)
   - `-v, --verbose`: Enable verbose output

## Hash Processing🔐
The project implements several key features for hash processing:

### Supported Hash Types
```python
hash_types = {
    32: "MD5",
    40: "SHA1",
    64: "SHA256",
    96: "SHA384",
    128: "SHA512"
}
```

### Hash Generation Process
```python
def generate_hash(password, hash_type='md5'):
    encoded = password.encode('utf-8')
    if hash_type == 'md5':
        return hashlib.md5(encoded).hexdigest()
    elif hash_type == 'sha1':
        return hashlib.sha1(encoded).hexdigest()
    # ... additional hash types
```

### Rate Limiting
The tool implements rate limiting to prevent resource exhaustion:
```python
class RateLimiter:
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.timestamps = []
```

## Examples📌

### Example 1: Creating Hash Database
```bash
python3 hash_create.py
```
Output:
```
Hashing Progress: 100%|██████████| 14344384/14344384 [00:45<00:00, 316543.62it/s]
Created all_hashes.txt
```

### Example 2: Cracking Single Hash
```bash
python3 hash.py -s 5f4dcc3b5aa765d61d8327deb882cf99
```
Output:
```
[+] MD5 -> 5f4dcc3b5aa765d61d8327deb882cf99: password
```
<p align="center">
  <img src="ex1.png" alt="Single Hash: 5f4dcc3b5aa765d61d8327deb882cf99" width="500">
  <br>
  <em>Single Hash: 5f4dcc3b5aa765d61d8327deb882cf99 </em>
</p>


### Example 3: Cracking Multiple Hashes
```bash
python3 hash.py -f hashes.txt -t 8
```
Output:
```
[*] Reading hashes from file: hashes.txt
[!] Found 100 unique hashes
[*] Starting crack with 8 threads

[+] Successfully cracked: 75/100 (75.0%)
[+] Results saved to cracked-hashes.txt
```

Note: The tool includes several features to enhance functionality:
- Multi-threading support for faster processing
- Color-coded output for better readability
- Progress tracking for bulk operations
- Automatic hash type detection
- Local hash database support
- Result saving functionality

These features make the tool efficient for both educational purposes and practical hash cracking exercises while maintaining a focus on performance and usability.
