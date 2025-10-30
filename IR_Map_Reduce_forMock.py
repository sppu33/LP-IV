# MapReduce Program to count occurrences of each alphabet character

# Import required modules
from multiprocessing import Pool, cpu_count   # For parallel processing (Map step)
from collections import Counter               # For counting occurrences easily

# ---------- Mapper Function ----------
def mapper(text_chunk):
    """
    Mapper function:
    Takes a chunk of text and returns a Counter (dictionary-like object)
    that counts how many times each alphabet letter appears in that chunk.
    """
    # Convert text to lowercase, keep only alphabets (ignore digits/symbols)
    return Counter(c for c in text_chunk.lower() if c.isalpha())


# ---------- Reducer Function ----------
def reducer(counts_list):
    """
    Reducer function:
    Takes a list of Counters (from all mappers) and merges them into one.
    This combines results from all chunks to get total counts.
    """
    total = Counter()
    # Loop through each Counter from mapper results
    for counts in counts_list:
        total.update(counts)  # Add counts together
    return total  # Final combined count


# ---------- Main Program ----------
if __name__ == "__main__":

    # Step 1: Read input file path from user
    file_path = input("Enter path of the input text file: ").strip()

    # Step 2: Try reading the text file safely
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()  # Read entire file into a string
    except FileNotFoundError:
        print("Error: File not found!")
        exit(1)
    except Exception as e:
        print("Error reading file:", e)
        exit(1)

    # Step 3: Check if file is empty
    if not data.strip():
        print("File is empty.")
        exit(0)

    # Step 4: Split text into chunks for parallel processing
    num_workers = cpu_count()  # Get number of available CPU cores
    chunk_size = max(1, len(data) // num_workers)  # Divide data evenly among workers
    # Create list of text chunks
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    # ---------- Map Step ----------
    # Create a pool of worker processes equal to CPU count
    with Pool(processes=num_workers) as pool:
        # Each process runs the mapper() on one chunk
        mapped_results = pool.map(mapper, chunks)

    # ---------- Reduce Step ----------
    # Combine (reduce) all partial counts from mapper results
    final_counts = reducer(mapped_results)

    # ---------- Output Step ----------
    print("\nCharacter Frequency (A–Z):")
    # Sort alphabetically and print each letter with its count
    for letter, count in sorted(final_counts.items()):
        print(f"{letter.upper()} : {count}")
