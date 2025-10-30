import argparse
from collections import Counter
from multiprocessing import Pool, cpu_count

def mapper(chunk):
    """Counts characters in a chunk of text."""
    return Counter(c for c in chunk.lower() if c.isalpha())

def reducer(counts_list):
    """Merges all counters into a single one."""
    result = Counter()
    for counts in counts_list:
        result.update(counts)
    return result

if __name__ == "__main__":
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Count letter occurrences in a text file using MapReduce.")
    parser.add_argument("filepath", help="The path to the input text file.")
    args = parser.parse_args()

    # Read data from the specified file
    try:
        with open(args.filepath, 'r', encoding='utf-8') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{args.filepath}' was not found.")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
        
    if not data:
        print("The file is empty. Nothing to process.")
        exit(0)

    # Split into chunks for parallel processing
    num_workers = cpu_count()
    chunk_size = len(data) // num_workers or 1
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    # Map step (parallel)
    with Pool(processes=num_workers) as pool:
        mapped_counts = pool.map(mapper, chunks)

    # Reduce step
    final_counts = reducer(mapped_counts)

    # Print results (sorted by letter)
    print(f"Character counts for '{args.filepath}':")
    for letter, count in sorted(final_counts.items()):
        print(f"{letter}: {count}")
        
# python "C:\Users\dande\Downloads\LPIV\IR_Map_Reduce.py" "C:\Users\dande\Downloads\LPIV\mapreduceinput.txt"
