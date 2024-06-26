import os
import logging
import sys
import gzip
import json
import fnmatch
import mimetypes
import exiftool
from datetime import datetime
import multiprocessing
import xml.etree.ElementTree as ET
import yaml
import csv
import configparser

def generate_file_structure(start_path, excluded_patterns=None):
    if excluded_patterns is None:
        excluded_patterns = []

    def is_excluded(path):
        return any(fnmatch.fnmatch(os.path.basename(path), pattern) for pattern in excluded_patterns)

    def tree(dir_path, prefix="", is_last=True):
        contents = [d for d in os.listdir(dir_path) if not is_excluded(os.path.join(dir_path, d))]
        contents = sorted(contents, key=lambda x: (os.path.isfile(os.path.join(dir_path, x)), x.lower()))
        pointers = ["└── " if is_last else "├── "] if prefix else [""]
        
        for i, path in enumerate(contents):
            is_last_item = (i == len(contents) - 1)
            yield prefix + pointers[0] + path
            
            if os.path.isdir(os.path.join(dir_path, path)):
                extension = "    " if is_last else "│   "
                yield from tree(os.path.join(dir_path, path), prefix + extension, is_last_item)

    return "\n".join(tree(start_path))

def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_config_value(config, section, key, default=None):
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return default

# Define the end-of-file indicator
EOF_INDICATOR = "\\n---EOF---\\n"

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

def setup_logging(log_file=None, log_level=logging.INFO):
    logger = logging.getLogger('content_processor')
    logger.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def process_file_content(start_directory, file_path, compress=False, exiftool_path=None):
    try:
        with open(file_path, 'r', encoding='utf8') as file:
            content = file.read()
            if compress:
                content = gzip.compress(content.encode('utf-8'))
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

def export_json(data, output_file):
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

def export_csv(data, output_file):
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'path', 'size', 'created_at', 'modified_at', 'metadata', 'content'])
        for file in data['pages'][0]['files']:
            writer.writerow([
                file['name'],
                file['path'],
                file['size'],
                file['created_at'],
                file['modified_at'],
                json.dumps(file['metadata']),
                file['content']
            ])

def export_xml(data, output_file):
    root = ET.Element('content_processor_output')
    for page in data['pages']:
        page_elem = ET.SubElement(root, 'page')
        page_elem.set('number', str(page['page']))
        for file in page['files']:
            file_elem = ET.SubElement(page_elem, 'file')
            for key, value in file.items():
                elem = ET.SubElement(file_elem, key)
                if isinstance(value, dict):
                    elem.text = json.dumps(value)
                else:
                    elem.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='unicode', xml_declaration=True)

def export_yaml(data, output_file):
    with open(output_file, 'w') as f:
        yaml.dump(data, f)

def main(start_directory, config_file=None, **kwargs):
    logger = setup_logging(None, logging.INFO)

    if config_file and os.path.exists(config_file):
        config = load_config(config_file)
        compress = get_config_value(config, 'Processing', 'compress', 'False').lower() == 'true'
        parallel = get_config_value(config, 'Processing', 'parallel', 'False').lower() == 'true'
        page_size = int(get_config_value(config, 'Output', 'page_size', '100'))
        exclude_patterns = get_config_value(config, 'Exclusion', 'patterns', '').split(',')
        exiftool_path = get_config_value(config, 'Tools', 'exiftool_path', 'exiftool')
        output_format = get_config_value(config, 'Output', 'format', 'json')
        output_file = get_config_value(config, 'Output', 'file', 'output')
    else:
        compress = kwargs.get('compress', False)
        parallel = kwargs.get('parallel', False)
        page_size = kwargs.get('page_size', 100)
        exclude_patterns = kwargs.get('exclude_patterns', [])
        exiftool_path = kwargs.get('exiftool_path', 'exiftool')
        output_format = kwargs.get('output_format', 'json')
        output_file = kwargs.get('output_file', 'output')

    # Check if start directory exists
    if not os.path.isdir(start_directory):
        print(f"The specified start directory '{start_directory}' does not exist or is not a directory.")
        return

    exclude_patterns = exclude_patterns or []
    excluded_dirs = EXCLUDE_DIRS_DEFAULT.union(exclude_patterns)
    excluded_files = EXCLUDE_FILES_DEFAULT.union(exclude_patterns)

    # Create a list to store file metadata
    file_list = []

    file_structure = generate_file_structure(start_directory, exclude_patterns)
    # logger.info("File structure being processed:\n" + file_structure)
    
    # Process directory
    logger.info(f"Processing directory: {start_directory}")
    process_directory(start_directory, file_list, compress, excluded_dirs, excluded_files, parallel, exiftool_path)

    logger.info(f"Processed {len(file_list)} files")
    json_data = paginate_file_list(file_list, page_size)
    
    logger.info(f"Exporting data in {output_format} format to {output_file}")
    if output_format == 'json':
        export_json(json_data, f"{output_file}.json")
    elif output_format == 'csv':
        export_csv(json_data, f"{output_file}.csv")
    elif output_format == 'xml':
        export_xml(json_data, f"{output_file}.xml")
    elif output_format == 'yaml':
        export_yaml(json_data, f"{output_file}.yaml")
    else:
        print(f"Unsupported output format: {output_format}")
    
    logger.info("Processing completed successfully")