# Content Processor

ContentProcessor is a Python package that scans a directory and processes its contents, generating a structured JSON output with file metadata and content. It provides a convenient way to extract and organize information from a directory hierarchy.

## Features

- Traverses a directory and its subdirectories to process files
- Excludes specified directories and files from processing
- Generates a JSON output with file metadata (name, path, size, creation time, modification time, type) and content
- Supports optional compression of file content using gzip
- Allows pagination of the output JSON for handling large datasets
- Provides a command-line interface for easy execution

## Installation

To install ContentProcessor, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/your-username/ContentProcessor.git
```

2. Navigate to the project directory:
```bash
cd content_processor
```

3. Install the package using the Makefile:
- For Linux: `make install-linux`
- For macOS: `make install-macos`
- For Windows: `make install-windows`

## Usage

To use ContentProcessor, run the following command:

```bash 
content_processor <directory> [--compress] [--page-size <size>] [--exclude-dir <dir>] [--exclude-file <file>]
```

- `<directory>`: The directory to scan and process (required)
- `--compress`: Compress the file content (optional)
- `--page-size <size>`: Number of files per page in the output JSON (default: 100)
- `--exclude-dir <dir>`: Additional directory to exclude (can be specified multiple times)
- `--exclude-file <file>`: Additional file to exclude (can be specified multiple times)

Example:

```bash 
content_processor /path/to/directory --compress --page-size 50 --exclude-dir node_modules --exclude-file .env
```

## Next Improvements

Here are some potential improvements for ContentProcessor:

1. **Parallel Processing**: Implement parallel processing to speed up the scanning and processing of large directories. This can be achieved using Python's `multiprocessing` module or libraries like `concurrent.futures`.

2. **Recursive Exclusion**: Allow recursive exclusion of directories and files using wildcard patterns or regular expressions. This would provide more flexibility in specifying exclusion rules.

3. **Metadata Extraction**: Enhance the metadata extraction capabilities by supporting additional file types and extracting more relevant information based on the file type (e.g., image dimensions, video duration).

4. **Output Formats**: Support additional output formats besides JSON, such as CSV or XML, to cater to different use cases and interoperability requirements.

5. **Incremental Processing**: Implement incremental processing functionality, where the package can detect and process only the changes since the last run, instead of processing the entire directory every time.

6. **Error Handling**: Improve error handling and logging mechanisms to provide more informative error messages and facilitate debugging.

7. **Configuration File**: Allow users to specify configuration options (e.g., excluded directories and files) through a configuration file instead of command-line arguments, making it easier to manage and reuse settings.

8. **Integration with Other Systems**: Explore integration possibilities with other systems or platforms, such as databases or cloud storage services, to directly store or process the extracted data.

## Contributing

Contributions to ContentProcessor are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/your-username/ContentProcessor).

## License

This project is licensed under the [MIT License](LICENSE).