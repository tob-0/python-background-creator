from background_creator import Creator
from os.path import isdir
from pathlib import Path
import argparse

BG_TYPES = ['BLURRED', 'BLACK', 'WHITE', 'COLOR', 'BRIGHTEST', 'DARKEST']

arg_parser = argparse.ArgumentParser(
    description='Generate a background for an image with a specific aspect ratio.')
arg_parser.add_argument('-o', '--output-dir',
                        default='./output/', type=str, help='Output directory')
arg_parser.add_argument('-i', '--input', type=str,
                        help='Input file or folder', required=True)
arg_parser.add_argument('-a', '--aspect-ratio', type=str,
                        help='Aspect ratio of the background')
arg_parser.add_argument('-t', '--type', type=str,
                        help='Type of background', choices=BG_TYPES, default='BLURRED')
arg_parser.add_argument(
    '-s', '--save', action='store_true', default=False, help='Save the output')
arg_parser.add_argument(
    '-v', '--verbose', action='store_true', help='Verbose output')


def main(args):

    files = []
    input_path = Path(args.input)
    if input_path.is_dir():
        content = input_path.iterdir()
        for obj in content:
            if obj.is_file():
                file_extension = obj.name.split('.')[-1]
                if file_extension in ['jpg']:
                    files += [str(obj.absolute())]

    else:
        if input_path.is_file():
            file_extension = input_path.name.split('.')[-1]
            if file_extension in ['jpg']:
                files += [input_path.absolute()]
        files += [args.input]
    aspect_ratio = args.aspect_ratio or '4/5'
    creator = Creator(verbose=args.verbose, aspect_ratio=aspect_ratio)

    for file in files:
        creator.generate(file, background_type=args.type,
                         save=args.save, save_folder=args.output_dir)


if __name__ == '__main__':
    main(arg_parser.parse_args())
