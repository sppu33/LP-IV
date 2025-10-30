"""
Assignment B5: XML Data Processing
This program reads an XML file and displays its contents.
"""

# Import the XML processing library
import xml.etree.ElementTree as ET

# -------------------------------
# Function: Parse and Display XML
# -------------------------------
def parse_and_display_xml(file_path):
    """
    Parses an XML file and prints its content in a structured way.

    Args:
        file_path (str): The path to the XML file.
    """
    try:
        # Load and parse the XML file
        tree = ET.parse(file_path)

        # Get the root element (top-level tag)
        root = tree.getroot()

        print("--- Processing Library Data from XML ---")

        # Loop through each <book> element in the XML
        for i, book in enumerate(root.findall('book')):
            # Get 'id' attribute from <book> tag
            book_id = book.get('id')

            # Extract text inside each child tag
            author = book.find('author').text
            title = book.find('title').text
            genre = book.find('genre').text
            price = book.find('price').text
            publish_date = book.find('publish_date').text

            # Print formatted book details
            print(f"\n--- Book {i+1} (ID: {book_id}) ---")
            print(f"  Title: {title}")
            print(f"  Author: {author}")
            print(f"  Genre: {genre}")
            print(f"  Price: ${price}")
            print(f"  Publish Date: {publish_date}")

        print("\n--- XML Processing Complete ---")

    # Handle errors (if file not found or invalid XML)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except ET.ParseError:
        print(f"Error: Could not parse '{file_path}'. Check if it is a valid XML file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# -------------------------------
# Main Function
# -------------------------------
def main():
    """
    Main function to start the XML parsing.
    """
    # Path of the XML file
    xml_file = 'C:/Users/dande/Downloads/LPIV/Myxml.xml'
    
    # Call the parsing function
    parse_and_display_xml(xml_file)


# Run the program
if __name__ == "__main__":
    main()
