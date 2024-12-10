"""RP To-Do entry point script."""
# rptodo/__main__.py

from app import cli, __application__

def main():
    cli.app(prog_name=__application__)

if __name__ == "__main__":
    main()