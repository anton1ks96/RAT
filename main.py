import argparse
from interface import cli_interface, telegram_interface

def main():
    parser = argparse.ArgumentParser(
        description="Псевдо RAG-система."
    )
    parser.add_argument(
        '--mode', choices=['cli', 'tg'], default='cli',
        help="Режим работы: cli (терминал) или tg (Telegram бот)"
    )
    args = parser.parse_args()

    if args.mode == 'cli':
        cli_interface.run_cli()
    elif args.mode == 'tg':
        telegram_interface.run_telegram_bot()

if __name__ == "__main__":
    main()
