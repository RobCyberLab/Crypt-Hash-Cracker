#!/usr/bin/env python3

# Import required libraries
import re                           # For regular expressions
import requests                     # For HTTP requests
import argparse                     # For command line argument parsing
import concurrent.futures           # For multi-threading processing
import urllib3                     # For HTTPS warning management
import time                        # For time-related functions
from typing import Optional, Tuple  # For type hints

# Disable warnings for invalid SSL certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define colors for output
class Colors:
    END = '\033[0m'      # Reset color
    RED = '\033[91m'     # Red for errors
    GREEN = '\033[92m'   # Green for success
    YELLOW = '\033[93m'  # Yellow for warnings
    BLUE = '\033[94m'    # Blue for information
    PURPLE = '\033[95m'  # Purple for hashes
    CYAN = '\033[96m'    # Cyan for general information

# Status indicators with colors
INFO = f"{Colors.YELLOW}[!]{Colors.END}"  # For information
GOOD = f"{Colors.GREEN}[+]{Colors.END}"   # For success
BAD = f"{Colors.RED}[-]{Colors.END}"      # For failure
RUN = f"{Colors.BLUE}[*]{Colors.END}"     # For running process

class RateLimiter:
    """
    Class for limiting request rates
    Used to prevent service overload
    """
    def __init__(self, calls: int, period: float):
        self.calls = calls          # Maximum number of allowed calls
        self.period = period        # Time period (in seconds)
        self.timestamps = []        # List of timestamps for calls

    def wait(self):
        """Wait if rate limit is exceeded"""
        now = time.time()
        # Keep only timestamps from current period
        self.timestamps = [t for t in self.timestamps if now - t <= self.period]
        
        if len(self.timestamps) >= self.calls:
            sleep_time = self.timestamps[0] + self.period - now
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.timestamps.append(now)

class HashCracker:
    """Main class for cracking hashes"""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the cracker
        :param verbose: If True, displays detailed messages
        """
        self.verbose = verbose

    def print_verbose(self, message: str):
        """
        Display messages in verbose mode
        :param message: Message to display
        """
        if self.verbose:
            print(f"{INFO} {message}")

    def identify_hash_type(self, hashvalue: str) -> str:
        """
        Identify hash type based on length
        :param hashvalue: Hash to identify
        :return: Hash type or "Unknown"
        """
        hash_length = len(hashvalue)
        hash_types = {
            32: "MD5",
            40: "SHA1",
            64: "SHA256",
            96: "SHA384",
            128: "SHA512"
        }
        return hash_types.get(hash_length, "Unknown")

    def check_local_hashes(self, hashvalue: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Search for hash in local hash file
        :param hashvalue: Hash to search for
        :return: (plain_text, hash_type) or (None, hash_type)
        """
        hash_type = self.identify_hash_type(hashvalue)
        try:
            with open("all_hashes.txt", "r") as file:
                for line in file:
                    if ":" in line:
                        plain, hashed = line.strip().split(":", 1)
                        if hashed == hashvalue:
                            self.print_verbose(f"Found in local file: {Colors.GREEN}{plain}{Colors.END}")
                            return plain, hash_type
        except FileNotFoundError:
            self.print_verbose(f"{Colors.RED}Local file 'all_hashes.txt' not found{Colors.END}")
        except Exception as e:
            self.print_verbose(f"{Colors.RED}Error reading local file: {str(e)}{Colors.END}")
        return None, hash_type

    def crack_hash(self, hashvalue: str) -> Tuple[Optional[str], str]:
        """
        Try to crack a hash using local file
        :param hashvalue: Hash to crack
        :return: (plain_text, hash_type) or (None, hash_type)
        """
        # Check in local file
        result, hash_type = self.check_local_hashes(hashvalue)
        if result:
            return result, hash_type

        hash_length = len(hashvalue)
        hash_type = self.identify_hash_type(hashvalue)
        
        if hash_type == "Unknown":
            self.print_verbose(f"{Colors.RED}Unknown hash type for length {hash_length}{Colors.END}")
            return None, hash_type

        self.print_verbose(f"Detected hash type: {Colors.CYAN}{hash_type}{Colors.END}")
        return None, hash_type

def print_banner():
    """Display application banner"""
    banner = f"""{Colors.CYAN}
╔═══════════════════════════════════════╗
║             Hash Cracker              ║
║              Word List                ║
╚═══════════════════════════════════════╝{Colors.END}
"""
    print(banner)

def main():
    """Main program function"""
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="Simple Hash Cracker")
    parser.add_argument("-s", "--hash", help="Single hash to crack")
    parser.add_argument("-f", "--file", help="File containing hashes")
    parser.add_argument("-t", "--threads", type=int, default=4, help="Number of threads")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print_banner()

    # Initialize cracker
    cracker = HashCracker(verbose=args.verbose)

    # Process single hash
    if args.hash:
        result, hash_type = cracker.crack_hash(args.hash)
        if result:
            print(f"{GOOD} {Colors.GREEN}{hash_type}{Colors.END} -> {Colors.PURPLE}{args.hash}{Colors.END}: {Colors.GREEN}{result}{Colors.END}")
        else:
            print(f"{BAD} {Colors.GREEN}{hash_type}{Colors.END} -> {Colors.PURPLE}{args.hash}{Colors.END}: {Colors.RED}Not found{Colors.END}")
        return

    # Process file with hashes
    if args.file:
        print(f"{RUN} Reading hashes from file: {Colors.CYAN}{args.file}{Colors.END}")
        # Read and extract hashes from file using regex
        with open(args.file) as f:
            hashes = set(re.findall(r'[a-f0-9]{128}|[a-f0-9]{96}|[a-f0-9]{64}|[a-f0-9]{40}|[a-f0-9]{32}', f.read()))
        
        print(f"{INFO} Found {Colors.CYAN}{len(hashes)}{Colors.END} unique hashes")
        print(f"{RUN} Starting crack with {Colors.CYAN}{args.threads}{Colors.END} threads\n")

        results = {}
        total_hashes = len(hashes)
        cracked_count = 0

        # Multi-threaded processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_hash = {executor.submit(cracker.crack_hash, h): h for h in hashes}
            completed = 0
            for future in concurrent.futures.as_completed(future_to_hash):
                completed += 1
                hash_value = future_to_hash[future]
                try:
                    result, hash_type = future.result()
                    if result:
                        results[hash_value] = (result, hash_type)
                        cracked_count += 1
                        print(f"{GOOD} {Colors.GREEN}{hash_type}{Colors.END} -> {Colors.PURPLE}{hash_value}{Colors.END}: {Colors.GREEN}{result}{Colors.END}")
                    else:
                        print(f"{BAD} {Colors.GREEN}{Colors.END}{Colors.PURPLE}{hash_value}{Colors.END}: {Colors.RED}Not found{Colors.END}")
                except Exception as exc:
                    print(f"{BAD} Error cracking {hash_value}: {str(exc)}")

        # Display success rate
        print(f"\n{GOOD} Successfully cracked: {Colors.CYAN}{cracked_count}/{total_hashes} ({(cracked_count / total_hashes) * 100:.1f}%)")
        
        # Save results to file
        if results:
            output_file = "cracked-hashes.txt"
            with open(output_file, "w") as f:
                for hash_value, (plain_text, hash_type) in results.items():
                    f.write(f"{plain_text}:{hash_value}:{hash_type}\n")
            print(f"{GOOD} Results saved to {Colors.CYAN}{output_file}{Colors.END}")
        else:
            print(f"{BAD} No hashes were cracked.")

# Program entry point
if __name__ == "__main__":
    main()