import logging
from src.bot import bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def main() -> None:
    bot()


if __name__ == '__main__':
    main()
