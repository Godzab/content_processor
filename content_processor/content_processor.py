import os
import gzip
import json
import fnmatch
import mimetypes
import exiftool
from datetime import datetime
import multiprocessing
import argparse

# Define the end-of-file indicator
EOF_INDICATOR = "\n---EOF---\n"

# Default exclusion patterns
EXCLUDE_DIRS_DEFAULT = {
    "node_modules", "build", ".git", ".svn", "dist",
    "__pycache__", ".pytest_cache", "venv", ".vscode", "vendor",
    ".idea", "bin", "obj", ".DS_Store", "tmp"
}

EXCLUDE_FILES_DEFAULT = {
    ".DS_Store", ".env", ".env.local", ".env.docker", ".env.docker.testing", 
    ".gitignore", ".gitkeep", ".gitattributes", ".gitmodules", "package-lock.json", 
    "package.json", "vendor", "composer.lock", "requirements.txt", "yarn.lock", 
    "yarn-error.log", "composer-lock.json", "yarn-debug.log", "access_log", 
    "error_log"
}

# Function to append file content with metadata to the in-memory buffer
def process_file_content(start_directory, file_path, compress=False, exiftool_path=None):
    try:
         with open(file_path, 'r', encoding='utf8') as file:
            content = file.read()
            if compress:
                content = gzip.compress(content)
                content = content.hex()  # Convert compressed content to hexadecimal string
           
            # Determine the file type using mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)

            # Extract metadata based on the file type
            metadata = {}
            if mime_type:
                metadata['type'] = mime_type

                # Extract additional metadata using exiftool
                with exiftool.ExifTool() as et:
                    metadata_raw = et.execute(b"-j", file_path.encode())
                    metadata.update(json.loads(metadata_raw)[0])

            file_metadata = {
                "name": os.path.basename(file_path),
                "path": os.path.relpath(file_path, start_directory),
                "size": os.path.getsize(file_path),
                "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                "modified_at": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                "metadata": metadata,
                "content": content
            }
            return file_metadata
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def is_excluded(path, exclude_patterns):
    """Checks if the path matches any of the exclude patterns."""
    return any(fnmatch.fnmatch(path, pattern) for pattern in exclude_patterns)

def process_directory(start_directory, file_list, compress, excluded_dirs, excluded_files, parallel, exiftool_path):
    if parallel:
        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
            for root, dirs, files in os.walk(start_directory):
                # Modify dirs in-place to skip excluded directories
                dirs[:] = [d for d in dirs if not is_excluded(d, excluded_dirs)]
                
                file_paths = [os.path.join(root, filename) for filename in files if not is_excluded(filename, excluded_files)]
                results = pool.starmap(process_file_content, [(start_directory, file_path, compress, exiftool_path) for file_path in file_paths])
                
                file_list.extend(filter(None, results))
    else:
        for root, dirs, files in os.walk(start_directory):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if not is_excluded(d, excluded_dirs)]
            
            for filename in files:
                file_path = os.path.join(root, filename)
                if not is_excluded(filename, excluded_files):
                    file_metadata = process_file_content(start_directory, file_path, compress, exiftool_path)
                    if file_metadata:
                        file_list.append(file_metadata)

def paginate_file_list(file_list, page_size):
    total_pages = (len(file_list) + page_size - 1) // page_size
    json_pages = []
    for page_number in range(total_pages):
        start_index = page_number * page_size
        end_index = min(start_index + page_size, len(file_list))
        page_files = file_list[start_index:end_index]

        # Convert file content back to a string if it's bytes
        for file in page_files:
            if isinstance(file['content'], bytes):
                file['content'] = file['content']

        json_page = {
            "page": page_number + 1,
            "total_pages": total_pages,
            "files": page_files
        }
        json_pages.append(json_page)
    return {"pages": json_pages}

def main(start_directory, compress=False, parallel=False, page_size=100, exclude_patterns=None, exiftool_path='exiftool'):
    # Check if start directory exists
    if not os.path.isdir(start_directory):
        print(f"The specified start directory '{start_directory}' does not exist or is not a directory.")
        return

    exclude_patterns = exclude_patterns or []
    excluded_dirs = EXCLUDE_DIRS_DEFAULT.union(exclude_patterns)
    excluded_files = EXCLUDE_FILES_DEFAULT.union(exclude_patterns)

    # Create a list to store file metadata
    file_list = []
    
    # Process directory
    process_directory(start_directory, file_list, compress, excluded_dirs, excluded_files, parallel, exiftool_path)

    # Paginate the file list
    json_data = paginate_file_list(file_list, page_size)
    
    # Output the final JSON data
    print(json.dumps(json_data, indent=2))