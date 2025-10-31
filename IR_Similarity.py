import math          # For mathematical operations like sqrt and acos
import string        # For string constants (punctuation, uppercase letters, etc.)
import sys           # For system exit if file read fails
import re

# ---------- Function: Read file ----------
def read_file(filename):
    """
    Reads the content of a text file and returns it as a string.
    Handles errors if file is missing or unreadable.
    """
    try:
        with open(filename, 'r') as f:
            data = f.read()       # Read entire file content
        return data
    except IOError:
        print("Error opening or reading input file:", filename)
        sys.exit()                # Exit program if file can't be read


# ---------- Create a translation table ----------
# Replace punctuation with spaces, and convert uppercase to lowercase
# translation_table = str.maketrans(
#     string.punctuation + string.ascii_uppercase,
#     " " * len(string.punctuation) + string.ascii_lowercase
# )


# ---------- Function: Convert text to list of words ----------
def get_words_from_line_list(text):
    # """
    # Cleans and splits text into words.
    # - Removes punctuation
    # - Converts to lowercase
    # - Splits text by spaces
    # """
    # text = text.translate(translation_table)  # Apply translation table
    # word_list = text.split()                  # Split into individual words
    # return word_list

# import re

# def get_words_from_text_simple(text):
    """
    Converts raw text into a clean list of words using regular expressions.
    """
    # 1. Convert to lowercase
    text = text.lower()
    
    # 2. Use re.findall to find all sequences of one or more letters/digits
    # This automatically ignores punctuation and splits the words.
    word_list = re.findall(r'\b[a-z0-9]+\b', text)
    
    return word_list

# ---------- Function: Count frequency of each word ----------
def count_frequency(word_list):
    """
    Counts how many times each word appears in the list.
    Returns a dictionary {word: frequency}.
    """
    D = {}
    for new_word in word_list:
        if new_word in D:
            D[new_word] += 1    # If word already seen, increase count
        else:
            D[new_word] = 1     # If new word, initialize count to 1
    return D


# ---------- Function: Process file and return frequency mapping ----------
def word_frequencies_for_file(filename):
    """
    Reads file, cleans it, counts word frequencies, and prints stats.
    Returns the word frequency dictionary.
    """
    line_list = read_file(filename)
    word_list = get_words_from_line_list(line_list)
    freq_mapping = count_frequency(word_list)

    print("File", filename, ":")
    print(len(line_list), "characters")
    print(len(word_list), "words")
    print(len(freq_mapping), "distinct words")

    return freq_mapping


# ---------- Function: Compute dot product of two word-frequency dictionaries ----------
def dotProduct(D1, D2):
    """
    Computes the dot product of two word frequency dictionaries.
    Sum of (word1_count * word2_count) for words present in both.
    """
    Sum = 0.0
    for key in D1:
        if key in D2:
            Sum += D1[key] * D2[key]
    return Sum


# ---------- Function: Compute angle between document vectors ----------
def vector_angle(D1, D2):
    """
    Calculates cosine similarity angle (in radians) between two frequency vectors.
    Smaller angle = more similar documents.
    """
    numerator = dotProduct(D1, D2)
    denominator = math.sqrt(dotProduct(D1, D1) * dotProduct(D2, D2))
    return math.acos(numerator / denominator)


# ---------- Main Function: Compare two documents ----------
def documentSimilarity(filename_1, filename_2):
    """
    Computes and prints the similarity (angle in radians)
    between two text documents.
    """
    sorted_word_list_1 = word_frequencies_for_file(filename_1)
    sorted_word_list_2 = word_frequencies_for_file(filename_2)
    distance = vector_angle(sorted_word_list_1, sorted_word_list_2)
    print("The distance between the documents is: %0.6f radians" % distance)


# ---------- Run program ----------
documentSimilarity('sample1.txt', 'sample2.txt')
