import argparse
import inquirer
from .content_processor import main

def interactive_mode():
    questions = [
        inquirer.Path('directory', message="Directory to scan", path_type=inquirer.Path.DIRECTORY),
        inquirer.Confirm('compress', message="Compress file content", default=False),
        inquirer.Confirm('parallel', message="Run processing in parallel", default=False),
        inquirer.Text('page_size', message="Number of files per page", default="100"),
        inquirer.Checkbox('exclude', message="Exclude patterns", choices=['node_modules', '.git', 'venv']),
        inquirer.List('output_format', message="Output format", choices=['json', 'csv', 'xml', 'yaml']),
        inquirer.Text('output_file', message="Output file name (without extension)", default="output"),
    ]
    answers = inquirer.prompt(questions)
    if answers:
        main(
            answers['directory'], compress=answers['compress'], parallel=answers['parallel'], 
            page_size=int(answers['page_size']), exclude_patterns=answers['exclude'], 
            output_format=answers['output_format'], output_file=answers['output_file'], 
        )

def run():
    parser = argparse.ArgumentParser(description='Scan a directory and process its contents.')

    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    args, unknown = parser.parse_known_args()
    
    if args.interactive:
        interactive_mode()
    else:
        parser.add_argument('directory', type=str, help='Directory to scan')
        parser.add_argument('--compress', action='store_true', help='Compress file content')
        parser.add_argument('--parallel', action='store_true', help='Run processing in parallel')
        parser.add_argument('--page-size', type=int, default=100, help='Number of files per page')
        parser.add_argument('--exclude', action='append', help='Exclude pattern (can be specified multiple times)')
        parser.add_argument('--output-format', choices=['json', 'csv', 'xml', 'yaml'], default='json', help='Output format')
        parser.add_argument('--output-file', default='output', help='Output file name (without extension)')
        parser.add_argument('--config', help='Path to configuration file')
    
        args = parser.parse_args()
        main(args.directory, config_file=args.config, compress=args.compress, parallel=args.parallel, page_size=args.page_size, exclude_patterns=args.exclude, output_format=args.output_format, output_file=args.output_file)

if __name__ == "__main__":
    run()