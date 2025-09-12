import pandas as pd
import os
import re
import io
import argparse  # Import the argparse library

def get_rst_path_from_url(url, base_path=""):
    """
    Converts a documentation URL to a local .rst file path.

    Args:
        url (str): The full URL from the CSV file.
        base_path (str): The base directory of the documentation source.

    Returns:
        str: The relative file path for the .rst file or None if URL is invalid.
    """
    if not isinstance(url, str):
        return None

    # Define the parts of the URL to strip
    prefix = "https://docs.alation.com/en/latest/"
    suffix = ".html"

    # Clean the URL to get the core path
    if url.startswith(prefix):
        relative_path = url[len(prefix):]
    else:
        # If the prefix doesn't match, we can't determine the path
        print(f"Warning: URL does not have the expected prefix. Skipping URL: {url}")
        return None

    if url.endswith(suffix):
        relative_path = relative_path[:-len(suffix)]
    
    # Construct the final .rst file path
    rst_file = f"{relative_path}.rst"
    
    # Join with the base path if one is provided
    full_path = os.path.join(base_path, rst_file)
    
    return full_path

def add_metadata_to_file(file_path, metadata):
    """
    Adds a formatted .. meta:: directive to an .rst file just after the title.

    Args:
        file_path (str): The path to the .rst file to be modified.
        metadata (dict): A dictionary containing the metadata to add.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Warning: File not found at '{file_path}'. Skipping.")
        return
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return

    # Find the page header, which is underlined with '=' characters.
    underline_index = -1
    for i in range(1, len(lines)):
        line_content = lines[i].strip()
        # Only match lines that consist solely of '=' characters.
        if line_content and all(c == '=' for c in line_content):
            # Ensure the line above it (the title) is not blank.
            if lines[i-1].strip():
                underline_index = i
                break
    
    if underline_index == -1:
        print(f"Warning: Could not find a page header underlined with '=' in '{file_path}'. Skipping.")
        return

    # Check if a meta directive already exists to avoid duplication
    if any(".. meta::" in line for line in lines):
        print(f"Info: A '.. meta::' directive already exists in '{file_path}'. Skipping to avoid duplication.")
        return

    # --- NEW METADATA BLOCK GENERATION ---
    meta_lines_to_add = []
    
    # Define the order and mapping from the CSV to the directive fields
    field_mapping = {
        'Deployment Type': 'deployment_type',
        'User Role': 'user_role',
        'Functional Area': 'functional_area',
        'Topics': 'topics',
    }

    for csv_key, meta_key in field_mapping.items():
        value = metadata.get(csv_key)
        if pd.notna(value) and str(value).strip():
            # Sanitize the value: replace semicolons and normalize comma spacing.
            sanitized_value_str = str(value).replace(';', ',')
            # Split by comma, strip whitespace from each part, and join with ", "
            items = [item.strip() for item in sanitized_value_str.split(',') if item.strip()]
            final_value = ", ".join(items)
            meta_lines_to_add.append(f"\t:{meta_key}: {final_value}")
            
    # Handle the "Keywords" column
    keywords = metadata.get('Keywords')
    if pd.notna(keywords) and str(keywords).strip():
        # Split by comma, strip whitespace, ensure uniqueness, and re-join
        unique_keywords = sorted(list({k.strip() for k in str(keywords).split(',') if k.strip()}))
        if unique_keywords:
            meta_lines_to_add.append(f"\t:keywords: {', '.join(unique_keywords)}")

    # Construct the final block if we have any metadata to add
    if meta_lines_to_add:
        full_meta_block = "\n" + ".. meta::\n" + "\n".join(meta_lines_to_add) + "\n"
        lines.insert(underline_index + 1, full_meta_block)
    else:
        print(f"Info: No metadata to add for '{file_path}'. Skipping.")
        return

    # Write the modified content back to the file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Successfully added metadata to {file_path}")
    except IOError as e:
        print(f"Error: Could not write to file '{file_path}': {e}")


def main():
    """
    Main function to drive the script. Reads a CSV and updates .rst files.
    """
    # --- MODIFIED SECTION ---
    # Set up argument parser to accept a filename from the command line
    parser = argparse.ArgumentParser(description="Inject metadata from a CSV file into Sphinx .rst files.")
    parser.add_argument("csv_file", help="The path to the input CSV file.")
    args = parser.parse_args()

    csv_file = args.csv_file  # Use the filename provided by the user
    
    if not os.path.exists(csv_file):
        print(f"Error: The file '{csv_file}' was not found.")
        return

    print(f"Reading and cleaning metadata from '{csv_file}'...")
    try:
        # Pre-process the CSV in memory to fix formatting issues from Google Sheets.
        cleaned_data = io.StringIO()
        with open(csv_file, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                # Check if the entire line is wrapped in quotes
                if stripped_line.startswith('"') and stripped_line.endswith('"'):
                    # Remove the outer quotes
                    cleaned_line = stripped_line[1:-1]
                    # Also, un-escape the double-quotes used for fields inside
                    cleaned_line = cleaned_line.replace('""', '"')
                    cleaned_data.write(cleaned_line + '\n')
                else:
                    # If not, write the line as-is
                    cleaned_data.write(line)
        
        # Move the buffer's cursor to the beginning to be read by pandas
        cleaned_data.seek(0)
        
        # Read the cleaned data from the in-memory buffer
        df = pd.read_csv(cleaned_data)

    except Exception as e:
        print(f"Error: Could not parse the CSV file. Please ensure it is formatted correctly. Details: {e}")
        return

    # Define the columns that contain the metadata
    metadata_columns = [
        'Keywords', 'Topics', 'Functional Area', 'User Role', 'Deployment Type'
    ]
    
    doc_base_path = "" 

    print("Starting to process .rst files...")
    # Iterate through each row of the dataframe
    for index, row in df.iterrows():
        url = row.get('Page URL')
        if not url or pd.isna(url):
            print(f"Warning: Skipping row {index + 2} due to missing or invalid URL.")
            continue

        rst_path = get_rst_path_from_url(url, doc_base_path)
        
        if rst_path:
            # Create a dictionary of metadata for the current row
            metadata = {col: row.get(col) for col in metadata_columns}
            add_metadata_to_file(rst_path, metadata)
    
    print("\nProcessing complete.")


if __name__ == "__main__":
    main()
