import argparse
from .content_processor import main

def run():
    parser = argparse.ArgumentParser(description='Scan a directory and process its contents.')
    parser.add_argument('directory', type=str, help='Directory to scan')
    parser.add_argument('--compress', action='store_true', help='Compress file content')
    parser.add_argument('--page-size', type=int, default=100, help='Number of files per page')
    parser.add_argument('--exclude-dir', action='append', help='Additional directory to exclude (can be specified multiple times)')
    parser.add_argument('--exclude-file', action='append', help='Additional file to exclude (can be specified multiple times)')
    args = parser.parse_args()
    main(args.directory, args.compress, args.page_size, set(args.exclude_dir or []), set(args.exclude_file or []))

if __name__ == "__main__":
    run()