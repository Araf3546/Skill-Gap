"""
Registers a `flask create-admin` CLI command on the app.
Add this import + call in app.py's create_app(), after blueprints are registered:

    from src.cli import register_cli
    register_cli(app)

Usage:
    flask create-admin
"""
import click
import getpass
from flask.cli import with_appcontext
from src.database.models import Role
from src.security.user_service import UserService


@click.command("create-admin")
@with_appcontext
def create_admin():
    """Create an admin user (interactive, run locally/on server only)."""
    email = input("Admin email: ").strip()
    password = getpass.getpass("Admin password (hidden, type freely): ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        click.echo("❌ Passwords don't match.")
        return
    if len(password) < 8:
        click.echo("❌ Password must be at least 8 characters.")
        return

    user_service = UserService()
    try:
        admin = user_service.register(email=email, password=password, role=Role.ADMIN)
        click.echo(f"✅ Admin created: id={admin.id}, role={admin.role.value}")
    except ValueError as e:
        click.echo(f"❌ {e}")


def register_cli(app):
    app.cli.add_command(create_admin)