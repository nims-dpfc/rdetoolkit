import click

from rdetoolkit.cmd.command import InitCommand, VersionCommand


@click.group()
def cli() -> None:
    """CLI generates template projects for RDE structured programs."""


@click.command()
def init() -> None:
    """Output files needed to build RDE structured programs."""
    cmd = InitCommand()
    cmd.invoke()


@click.command()
def version() -> None:
    """Command to display version."""
    cmd = VersionCommand()
    cmd.invoke()


cli.add_command(init)
cli.add_command(version)
