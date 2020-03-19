import os
import click


def register(cli):
    @cli.command()
    def scrape():
        print("Scraping data...")
        import app.data
        print("Done")


if __name__ == '__main__':
    @click.group()
    def main_cli():
        pass

    register(main_cli)
    
    main_cli()
