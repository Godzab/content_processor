import argparse
from .content_processor import main

def run():
    parser = argparse.ArgumentParser(description='Scan a directory and process its contents.')
    parser.add_argument('directory', type=str, help='Directory to scan')
    parser.add_argument('--compress', action='store_true', help='Compress file content')
    parser.add_argument('--parallel', action='store_true', help='Run processing in parallel')
    parser.add_argument('--page-size', type=int, default=100, help='Number of files per page')
    parser.add_argument('--exclude', action='append', help='Exclude pattern (can be specified multiple times)')
    args = parser.parse_args()
    main(args.directory, args.compress, args.parallel, args.page_size, args.exclude)

if __name__ == "__main__":
    run()