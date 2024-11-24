import hashlib
import os
from tqdm import tqdm

def generate_hash(password, hash_type='md5'):
    """Generate hash for a given password and hash type."""
    encoded = password.encode('utf-8')
    if hash_type == 'md5':
        return hashlib.md5(encoded).hexdigest()
    elif hash_type == 'sha1':
        return hashlib.sha1(encoded).hexdigest()
    elif hash_type == 'sha256':
        return hashlib.sha256(encoded).hexdigest()
    elif hash_type == 'sha384':
        return hashlib.sha384(encoded).hexdigest()   
    elif hash_type == 'sha512':
        return hashlib.sha512(encoded).hexdigest()   

def load_passwords_from_file(wordlist_path):
    """Load passwords from a wordlist file."""
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Wordlist file '{wordlist_path}' not found.")
        return []
    except Exception as e:
        print(f"An error occurred while reading the wordlist: {e}")
        return []

def create_hash_file(wordlist_path):
    """Generate a single hash file containing all hashes with a progress bar."""
    # Load passwords from the provided wordlist
    passwords = load_passwords_from_file(wordlist_path)
    if not passwords:
        print("No passwords loaded. Exiting.")
        return
    
    # Define hash types with sha512 at the end
    hash_types = ['md5', 'sha1', 'sha256', 'sha384', 'sha512']
   
    # Create a combined file with all hash types
    combined_filename = 'all_hashes.txt'
    with open(combined_filename, 'w', encoding='utf-8') as f:
        with tqdm(total=len(passwords) * len(hash_types), desc="Hashing Progress") as pbar:
            for password in passwords:
                for hash_type in hash_types:
                    hash_value = generate_hash(password, hash_type)
                    f.write(f'{password}:{hash_value}\n')
                    pbar.update(1)  # Update the progress bar for each hash
    
    print(f"\nCreated {combined_filename}")

if __name__ == '__main__':
    # Provide the path to the RockYou wordlist or another wordlist file
    wordlist_path = 'rockyou.txt'  # Update the path if needed
    create_hash_file(wordlist_path)
