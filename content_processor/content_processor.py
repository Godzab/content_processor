import os
import io
import argparse
import gzip
import json
from datetime import datetime

# Define the end-of-file indicator
eof_indicator = "\n---EOF---\n"

# Define a set of directory names to exclude from the traversal
exclude_dirs = {
    "node_modules", "build", ".git", ".svn", "dist",
    "__pycache__", ".pytest_cache", "venv", ".vscode", "vendor",
    ".idea", "bin", "obj", ".DS_Store", "tmp"
}

# Define a set of files to exclude from the traversal
exclude_files = {
    ".DS_Store",".env",".env.local",".env.docker", ".env.docker.testing", ".gitignore", ".gitkeep", ".gitattributes",
    ".gitmodules", "package-lock.json", "package.json", "vendor", "composer.lock",
    "requirements.txt", "yarn.lock", "yarn-error.log", "composer-lock.json",
    "yarn-debug.log", "yarn-error.log", "yarn-debug.log","access_log", "error_log",
    "yarn.lock", "yarn-error.log", "yarn-debug.log","access.log", "error.log"
}

# Function to append file content with metadata to the in-memory buffer
def process_file_content(start_directory, file_path, buffer, compress=False):
    try:
        with open(file_path, 'r', encoding='utf8') as file:
            content = file.read()
            if compress:
                content = gzip.compress(content.encode('utf-8'))
                content = content.hex()  # Convert compressed content to hexadecimal string
            file_metadata = {
                "name": os.path.basename(file_path),
                "path": os.path.relpath(file_path, start_directory),
                "size": os.path.getsize(file_path),
                "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                "modified_at": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                "type": "text/plain",
                "content": content
            }
            buffer.append(file_metadata)
    except Exception as e:
        pass

def main(start_directory, compress=False, page_size=100, exclude_dirs=None, exclude_files=None):
    # Check if start directory exists
    if not os.path.isdir(start_directory):
        print(f"The specified start directory '{start_directory}' does not exist or is not a directory.")
        return

    # Merge default and user-specified excluded directories
    excluded_dirs = set(exclude_dirs) | exclude_dirs
    excluded_files = set(exclude_files) | exclude_files

    # Create a list to store file metadata
    file_list = []
    
    # Walk through the directory
    for root, dirs, files in os.walk(start_directory):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for filename in files:
            file_path = os.path.join(root, filename)
            # Skip excluded files
            if filename in excluded_files:
                continue
            # Skip certain types of files such as hidden files or specific extensions
            if not filename.startswith('.') and not filename.lower().endswith(('.log', '.tmp', '.png', '.ico')):
                process_file_content(start_directory, file_path, file_list, compress)

    # Paginate the file list
    total_pages = (len(file_list) + page_size - 1) // page_size
    for page_number in range(total_pages):
        start_index = page_number * page_size
        end_index = min(start_index + page_size, len(file_list))
        page_files = file_list[start_index:end_index]
        
        # Create the JSON structure for the current page
        json_data = {
            "page": page_number + 1,
            "total_pages": total_pages,
            "files": page_files
        }
        
        # Output the JSON data for the current page
        print(json.dumps(json_data, indent=2))