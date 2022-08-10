import argparse
import logging

from . import __version__, init, update, dump


def setup_log(log_level: str) -> None:
    if log_level == 'debug':
        _log_level = logging.DEBUG
    elif log_level == 'info':
        _log_level = logging.INFO
    elif log_level == 'error':
        _log_level = logging.ERROR
    else:
        raise ValueError(f"Invalid log-level value: '{log_level}'")

    root_logger = logging.getLogger()
    root_logger.setLevel(_log_level)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)


def main() -> None:
    # Define parser
    parser = argparse.ArgumentParser(
        prog='qmonus_plugin_builder',
        description='Qmonus-PluginBuilder',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )
    parser.add_argument(
        '--log-level',
        type=str,
        dest='log_level',
        choices=['debug', 'info', 'error'],
        default='info',
        help='log level',
    )

    sub_parser = parser.add_subparsers(dest='sub_parser')

    # Define init parser
    init_parser = sub_parser.add_parser(
        'init', 
        help='Initialize',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    init_parser.add_argument(
        'project_path',
        type=str,
        help='project directory path',
    )

    # Define update parser
    update_parser = sub_parser.add_parser(
        'update', 
        help='Update libs',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    update_parser.add_argument(
        'project_path',
        type=str,
        help='project directory path',
    )

    # Define dump parser
    dump_parser = sub_parser.add_parser(
        'dump',
        help='Convert python module to yaml',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    dump_parser.add_argument(
        'project_path',
        type=str,
        help='project directory path',
    )
    dump_parser.add_argument(
        'yaml_path',
        type=str,
        help='yaml directory path',
    )

    # Parse args
    args = parser.parse_args()
    if args.sub_parser is None:
        parser.print_help()
        exit(1)

    # Setup logging
    setup_log(log_level=args.log_level)
    logger = logging.getLogger(__name__)

    # Execute
    try:
        if args.sub_parser == 'init':
            init(project_path=args.project_path)
        elif args.sub_parser == 'update':
            update(project_path=args.project_path)
        elif args.sub_parser == 'dump':
            dump(project_path=args.project_path, yaml_path=args.yaml_path)

        print("Succeeded.")

    except Exception as e:
        logger.exception(e)
        print('\nFailed.')
        exit(1)


if __name__ == '__main__':
    main()
