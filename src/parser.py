from unified_bot.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["parse", *(__import__("sys").argv[1:])]))
