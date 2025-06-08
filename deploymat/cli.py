import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import asyncio

from .core import PyDockManager
from .settings import get_settings
from .utils import Logger
from .shell import interactive_shell
from .api.server import run_server
from .cloudflare import CloudflareManager
from .git import clone_git_repo, is_valid_git_url, validate_repo_for_deployment

# Initialize
app = typer.Typer(
    name="pydock",
    help="🐳 PyDock - Python Docker Deployment Manager",
    add_completion=False,
    rich_markup_mode="rich"
)
console = Console()
logger = Logger()
settings = get_settings()

# Subcommands
cloudflare_app = typer.Typer(help="☁️ Cloudflare DNS management")
git_app = typer.Typer(help="📂 Git operations")
api_app = typer.Typer(help="🚀 API server management")
env_app = typer.Typer(help="🔧 Environment management")

app.add_typer(cloudflare_app, name="cloudflare")
app.add_typer(git_app, name="git")
app.add_typer(api_app, name="api")
app.add_typer(env_app, name="env")


@app.command()
def init(
        domain: str = typer.Argument(..., help="Domain name (e.g., example.com)"),
        vps_ip: str = typer.Argument(..., help="VPS IP address"),
        ssh_key_path: Optional[str] = typer.Option(None, "--ssh-key", "-k", help="SSH key path"),
        config_file: str = typer.Option("pydock.json", "--config", "-c", help="Config file path"),
        generate_apps: bool = typer.Option(False, "--generate", "-g", help="Generate sample applications"),
):
    """🚀 Initialize new PyDock project"""
    try:
        manager = PyDockManager(config_file)

        console.print(f"🚀 Initializing PyDock project for [cyan]{domain}[/cyan]")

        manager.init_project(
            domain=domain,
            vps_ip=vps_ip,
            ssh_key_path=ssh_key_path
        )

        console.print(f"✅ Project initialized successfully!", style="green")

        if generate_apps:
            console.print("📁 Generating sample applications...")
            from .generators import generate_sample_app
            generate_sample_app('flask')
            generate_sample_app('static')
            console.print("✅ Sample applications generated!", style="green")

        # Show next steps
        panel = Panel(
            f"""1. Configure DNS records for [cyan]{domain}[/cyan]
2. Customize applications in [yellow]web-app/[/yellow] and [yellow]static-site/[/yellow]
3. Deploy with: [green]pydock deploy[/green]
4. Monitor with: [blue]pydock status[/blue]""",
            title="📋 Next Steps",
            border_style="blue"
        )
        console.print(panel)

    except Exception as e:
        console.print(f"❌ Initialization failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def deploy(
        environment: str = typer.Option("production", "--env", "-e", help="Target environment"),
        config_file: str = typer.Option("pydock.json", "--config", "-c", help="Config file path"),
        force: bool = typer.Option(False, "--force", "-f", help="Force deployment without confirmation"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deployed"),
):
    """🚀 Deploy application to VPS"""
    try:
        manager = PyDockManager(config_file)

        if not manager.config.exists():
            console.print("❌ No project found. Run [yellow]pydock init[/yellow] first.", style="red")
            raise typer.Exit(1)

        config = manager.config.load()
        domain = config.get("domain")

        if dry_run:
            console.print(f"🔍 Dry run mode - showing deployment plan for [cyan]{domain}[/cyan]")
            # TODO: Show deployment plan
            console.print("✅ Deployment plan ready", style="green")
            return

        if not force:
            confirm = typer.confirm(f"🚀 Deploy to {environment} environment for {domain}?")
            if not confirm:
                console.print("❌ Deployment cancelled", style="yellow")
                raise typer.Exit(0)

        console.print(f"🚀 Starting deployment to [cyan]{environment}[/cyan]...")

        manager.deploy(environment)

        console.print("🎉 Deployment completed successfully!", style="green")
        console.print(f"🌐 Your application is available at: [link]https://{domain}[/link]")

    except Exception as e:
        console.print(f"❌ Deployment failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def status(
        config_file: str = typer.Option("pydock.json", "--config", "-c", help="Config file path"),
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed status"),
):
    """📊 Show project status"""
    try:
        manager = PyDockManager(config_file)

        if not manager.config.exists():
            console.print("❌ No project found", style="red")
            raise typer.Exit(1)

        manager.status()

        if verbose:
            # Show additional details
            config = manager.config.load()

            table = Table(title="📋 Project Details")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Domain", config.get("domain", "Not set"))
            table.add_row("VPS IP", config.get("vps_ip", "Not set"))
            table.add_row("Environment", settings.environment)
            table.add_row("Services", str(len(config.get("services", {}))))

            console.print(table)

    except Exception as e:
        console.print(f"❌ Status check failed: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def logs(
        service: Optional[str] = typer.Argument(None, help="Service name (optional)"),
        follow: bool = typer.Option(False, "--follow", "-f", help="Follow logs in real-time"),
        lines: int = typer.Option(100, "--lines", "-n", help="Number of lines to show"),
        config_file: str = typer.Option("pydock.json", "--config", "-c", help="Config file path"),
):
    """📝 Show application logs"""
    try:
        manager = PyDockManager(config_file)

        if not manager.config.exists():
            console.print("❌ No project found", style="red")
            raise typer.Exit(1)

        console.print(f"📝 Showing logs for [cyan]{service or 'all services'}[/cyan]")
        manager.logs(service, follow)

    except KeyboardInterrupt:
        console.print("\n⚠️  Log streaming stopped", style="yellow")
    except Exception as e:
        console.print(f"❌ Failed to get logs: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def stop(
        config_file: str = typer.Option("pydock.json", "--config", "-c", help="Config file path"),
        force: bool = typer.Option(False, "--force", "-f", help="Force stop without confirmation"),
):
    """🛑 Stop all services"""
    try:
        manager = PyDockManager(config_file)

        if not manager.config.exists():
            console.print("❌ No project found", style="red")
            raise typer.Exit(1)

        if not force:
            confirm = typer.confirm("🛑 Stop all services?")
            if not confirm:
                console.print("❌ Operation cancelled", style="yellow")
                raise typer.Exit(0)

        manager.stop()
        console.print("✅ All services stopped", style="green")

    except Exception as e:
        console.print(f"❌ Failed to stop services: {e}", style="red")
        raise typer.Exit(1)


@app.command()
def shell():
    """🐚 Start interactive PyDock shell"""
    console.print("🐳 Starting PyDock interactive shell...", style="cyan")
    interactive_shell()


@app.command()
def generate(
        app_type: str = typer.Argument(..., help="Application type (app, static, api)"),
        output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """📁 Generate sample applications"""
    try:
        from .generators import generate_sample_app

        valid_types = ["app", "static", "api", "flask", "fastapi"]

        if app_type not in valid_types:
            console.print(f"❌ Invalid type. Choose from: {', '.join(valid_types)}", style="red")
            raise typer.Exit(1)

        console.print(f"📁 Generating [cyan]{app_type}[/cyan] application...")
        generate_sample_app(app_type)
        console.print(f"✅ {app_type} application generated successfully!", style="green")

    except Exception as e:
        console.print(f"❌ Generation failed: {e}", style="red")
        raise typer.Exit(1)


# Cloudflare commands
@cloudflare_app.command()
def zones(
        token: Optional[str] = typer.Option(None, "--token", "-t", help="Cloudflare API token"),
):
    """📋 List Cloudflare zones"""

    async def _list_zones():
        try:
            cf_token = token or settings.cloudflare_api_token
            if not cf_token:
                cf_token = typer.prompt("Enter Cloudflare API token", hide_input=True)

            cf_manager = CloudflareManager(cf_token)
            zones = await cf_manager.list_zones()

            table = Table(title="🌐 Cloudflare Zones")
            table.add_column("Name", style="cyan")
            table.add_column("ID", style="green")
            table.add_column("Status", style="yellow")

            for zone in zones:
                table.add_row(
                    zone.get("name", ""),
                    zone.get("id", ""),
                    zone.get("status", "")
                )

            console.print(table)

        except Exception as e:
            console.print(f"❌ Failed to list zones: {e}", style="red")
            raise typer.Exit(1)

    asyncio.run(_list_zones())


@cloudflare_app.command()
def setup(
        domain: Optional[str] = typer.Option(None, "--domain", "-d", help="Domain name"),
        vps_ip: Optional[str] = typer.Option(None, "--ip", help="VPS IP address"),
        token: Optional[str] = typer.Option(None, "--token", "-t", help="Cloudflare API token"),
):
    """⚙️ Setup DNS records for domain"""

    async def _setup_dns():
        try:
            # Get values from config if not provided
            if not domain or not vps_ip:
                manager = PyDockManager()
                if manager.config.exists():
                    config = manager.config.load()
                    domain_val = domain or config.get("domain")
                    ip_val = vps_ip or config.get("vps_ip")
                else:
                    domain_val = domain or typer.prompt("Enter domain name")
                    ip_val = vps_ip or typer.prompt("Enter VPS IP address")
            else:
                domain_val = domain
                ip_val = vps_ip

            cf_token = token or settings.cloudflare_api_token
            if not cf_token:
                cf_token = typer.prompt("Enter Cloudflare API token", hide_input=True)

            console.print(f"⚙️ Setting up DNS for [cyan]{domain_val}[/cyan] → [green]{ip_val}[/green]")

            cf_manager = CloudflareManager(cf_token)
            records = await cf_manager.setup_dns_records(domain_val, ip_val)

            console.print(f"✅ Configured {len(records)} DNS records successfully!", style="green")

        except Exception as e:
            console.print(f"❌ DNS setup failed: {e}", style="red")
            raise typer.Exit(1)

    asyncio.run(_setup_dns())


# Git commands
@git_app.command()
def clone(
        url: str = typer.Argument(..., help="Git repository URL"),
        directory: Optional[str] = typer.Option(None, "--dir", "-d", help="Target directory"),
        branch: Optional[str] = typer.Option(None, "--branch", "-b", help="Specific branch"),
):
    """📥 Clone Git repository"""
    try:
        if not is_valid_git_url(url):
            console.print(f"❌ Invalid Git URL: {url}", style="red")
            raise typer.Exit(1)

        target_dir = directory or Path(url).stem.replace('.git', '')

        console.print(f"📥 Cloning [cyan]{url}[/cyan] to [yellow]{target_dir}[/yellow]")

        success = clone_git_repo(url, target_dir, branch)

        if success:
            console.print("✅ Repository cloned successfully!", style="green")
        else:
            console.print("❌ Clone failed", style="red")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"❌ Clone failed: {e}", style="red")
        raise typer.Exit(1)


@git_app.command()
def validate(
        path: str = typer.Option(".", "--path", "-p", help="Repository path"),
):
    """🔍 Validate repository for deployment"""
    try:
        validation = validate_repo_for_deployment(path)

        if validation["valid"]:
            console.print("✅ Repository is ready for deployment!", style="green")
        else:
            console.print("❌ Repository has deployment issues", style="red")

        # Show detailed results
        if validation["errors"]:
            error_panel = Panel(
                "\n".join(f"• {error}" for error in validation["errors"]),
                title="❌ Errors",
                border_style="red"
            )
            console.print(error_panel)

        if validation["warnings"]:
            warning_panel = Panel(
                "\n".join(f"• {warning}" for warning in validation["warnings"]),
                title="⚠️ Warnings",
                border_style="yellow"
            )
            console.print(warning_panel)

        if validation["recommendations"]:
            rec_panel = Panel(
                "\n".join(f"• {rec}" for rec in validation["recommendations"]),
                title="💡 Recommendations",
                border_style="blue"
            )
            console.print(rec_panel)

    except Exception as e:
        console.print(f"❌ Validation failed: {e}", style="red")
        raise typer.Exit(1)


# API commands
@api_app.command()
def start(
        host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
        port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
        reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
):
    """🚀 Start API server"""
    try:
        console.print(f"🚀 Starting PyDock API server on [cyan]{host}:{port}[/cyan]")
        console.print(f"📖 Documentation: [link]http://{host}:{port}/docs[/link]")

        run_server(host=host, port=port, reload=reload)

    except KeyboardInterrupt:
        console.print("\n🛑 API server stopped", style="yellow")
    except Exception as e:
        console.print(f"❌ Server failed: {e}", style="red")
        raise typer.Exit(1)


# Environment commands
@env_app.command()
def init():
    """📝 Initialize .env file from template"""
    try:
        env_template = Path(".env.template")
        env_file = Path(".env")

        if not env_template.exists():
            console.print("❌ .env.template not found", style="red")
            raise typer.Exit(1)

        if env_file.exists():
            overwrite = typer.confirm(".env already exists. Overwrite?")
            if not overwrite:
                console.print("❌ Operation cancelled", style="yellow")
                raise typer.Exit(0)

        # Copy template to .env
        import shutil
        shutil.copy(env_template, env_file)

        console.print("✅ .env file created from template", style="green")
        console.print("📝 Please edit .env file with your values", style="cyan")

    except Exception as e:
        console.print(f"❌ Failed to create .env: {e}", style="red")
        raise typer.Exit(1)


@env_app.command()
def show():
    """👀 Show current environment variables"""
    table = Table(title="🔧 Environment Variables")
    table.add_column("Variable", style="cyan")
    table.add_column("Value", style="green")

    env_vars = [
        ("PYDOCK_DOMAIN", settings.domain),
        ("PYDOCK_VPS_IP", settings.vps_ip),
        ("PYDOCK_ENVIRONMENT", settings.environment),
        ("CLOUDFLARE_API_TOKEN", "***" if settings.cloudflare_api_token else "Not set"),
        ("API_SECRET_KEY", "***" if settings.api_secret_key else "Not set"),
    ]

    for var, value in env_vars:
        table.add_row(var, str(value or "Not set"))

    console.print(table)


@app.command()
def version():
    """📦 Show PyDock version"""
    from . import __version__

    panel = Panel(
        f"PyDock version [green]{__version__}[/green]\n"
        f"Python Docker Deployment Manager\n"
        f"Environment: [cyan]{settings.environment}[/cyan]",
        title="📦 Version Info",
        border_style="blue"
    )
    console.print(panel)


def main():
    """Main CLI entry point"""
    app()


if __name__ == "__main__":
    main()