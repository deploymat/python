import cmd
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from .core import PyDockManager
from .settings import get_settings
from .utils import Logger
from .cloudflare import CloudflareManager
from .git import get_repo_info, validate_repo_for_deployment


class PyDockShell(cmd.Cmd):
    """Interactive PyDock shell"""

    intro = '''
🐳 Welcome to PyDock Interactive Shell!
Type help or ? to list commands.
Type exit or quit to exit.
'''
    prompt = '(pydock) '

    def __init__(self):
        super().__init__()
        self.console = Console()
        self.logger = Logger()
        self.settings = get_settings()
        self.manager = None
        self.current_project = None

        # Try to load existing project
        self._load_current_project()

    def _load_current_project(self):
        """Load current project if exists"""
        if Path("pydock.json").exists():
            try:
                self.manager = PyDockManager()
                config = self.manager.config.load()
                self.current_project = config.get("domain", "Unknown")
                self.console.print(f"📁 Loaded project: {self.current_project}", style="green")
            except Exception as e:
                self.console.print(f"⚠️  Failed to load project: {e}", style="yellow")

    def _update_prompt(self):
        """Update prompt with current project"""
        if self.current_project:
            self.prompt = f'(pydock:{self.current_project}) '
        else:
            self.prompt = '(pydock) '

    def do_status(self, arg):
        """Show current project status"""
        if not self.manager:
            self.console.print("❌ No project loaded. Use 'init' or 'load' first.", style="red")
            return

        try:
            config = self.manager.config.load()

            # Create status table
            table = Table(title="📊 Project Status")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Domain", config.get("domain", "Not set"))
            table.add_row("VPS IP", config.get("vps_ip", "Not set"))
            table.add_row("Services", str(len(config.get("services", {}))))
            table.add_row("Environment", self.settings.environment)

            self.console.print(table)

            # Show services
            if config.get("services"):
                services_table = Table(title="🔧 Services")
                services_table.add_column("Name", style="cyan")
                services_table.add_column("Subdomain", style="green")
                services_table.add_column("Port", style="yellow")
                services_table.add_column("Type", style="magenta")

                for name, service in config["services"].items():
                    subdomain = service.get("subdomain", "N/A")
                    port = str(service.get("port", "N/A"))
                    service_type = "Build" if "build_path" in service else "Image"

                    services_table.add_row(name, subdomain, port, service_type)

                self.console.print(services_table)

        except Exception as e:
            self.console.print(f"❌ Generation failed: {e}", style="red")

    def do_env(self, arg):
        """Environment management
        Usage: env [show|set key value|load file]
        """
        args = arg.split()
        command = args[0] if args else "show"

        if command == "show":
            # Show current environment variables
            table = Table(title="🔧 Environment Variables")
            table.add_column("Variable", style="cyan")
            table.add_column("Value", style="green")

            env_vars = [
                ("PYDOCK_DOMAIN", self.settings.domain),
                ("PYDOCK_VPS_IP", self.settings.vps_ip),
                ("PYDOCK_ENVIRONMENT", self.settings.environment),
                ("CLOUDFLARE_API_TOKEN", "***" if self.settings.cloudflare_api_token else "Not set"),
                ("API_SECRET_KEY", "***" if self.settings.api_secret_key else "Not set"),
            ]

            for var, value in env_vars:
                table.add_row(var, str(value or "Not set"))

            self.console.print(table)

        elif command == "set" and len(args) >= 3:
            key = args[1]
            value = " ".join(args[2:])

            # Update environment variable
            import os
            os.environ[key] = value

            # Save to .env file
            try:
                env_file = Path(".env")
                env_content = ""

                if env_file.exists():
                    with open(env_file, 'r') as f:
                        env_content = f.read()

                # Update or add the variable
                lines = env_content.split('\n')
                updated = False

                for i, line in enumerate(lines):
                    if line.startswith(f"{key}="):
                        lines[i] = f"{key}={value}"
                        updated = True
                        break

                if not updated:
                    lines.append(f"{key}={value}")

                with open(env_file, 'w') as f:
                    f.write('\n'.join(lines))

                self.console.print(f"✅ Set {key}={value}", style="green")

            except Exception as e:
                self.console.print(f"❌ Failed to save to .env: {e}", style="red")

        elif command == "load":
            file_path = args[1] if len(args) > 1 else ".env"

            try:
                from dotenv import load_dotenv
                load_dotenv(file_path)
                self.console.print(f"✅ Loaded environment from {file_path}", style="green")

                # Reload settings
                from .settings import reload_settings
                reload_settings()

            except Exception as e:
                self.console.print(f"❌ Failed to load {file_path}: {e}", style="red")

        else:
            self.console.print("Usage: env [show|set key value|load file]", style="yellow")

    def do_server(self, arg):
        """Start/stop API server
        Usage: server [start|stop|status] [--port 8000]
        """
        args = arg.split()
        command = args[0] if args else "start"

        port = 8000
        if "--port" in args:
            port_idx = args.index("--port")
            if port_idx + 1 < len(args):
                port = int(args[port_idx + 1])

        if command == "start":
            self.console.print(f"🚀 Starting API server on port {port}...", style="cyan")
            self.console.print(f"📖 Documentation: http://localhost:{port}/docs", style="green")

            try:
                from .api.server import run_server
                run_server(port=port)
            except KeyboardInterrupt:
                self.console.print("\n🛑 Server stopped", style="yellow")
            except Exception as e:
                self.console.print(f"❌ Server failed: {e}", style="red")

        elif command == "status":
            # Check if server is running
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            if result == 0:
                self.console.print(f"✅ Server is running on port {port}", style="green")
            else:
                self.console.print(f"❌ Server is not running on port {port}", style="red")

        else:
            self.console.print("Usage: server [start|stop|status] [--port 8000]", style="yellow")

    def do_backup(self, arg):
        """Backup management
        Usage: backup [create|restore|list]
        """
        args = arg.split()
        command = args[0] if args else "list"

        if command == "create":
            backup_name = args[1] if len(args) > 1 else f"backup-{self.current_project or 'unknown'}"

            self.console.print(f"💾 Creating backup: {backup_name}", style="cyan")

            # TODO: Implement backup creation
            self.console.print("✅ Backup created (not implemented yet)", style="green")

        elif command == "list":
            # TODO: List available backups
            self.console.print("📋 Available backups (not implemented yet)", style="cyan")

        elif command == "restore":
            backup_name = args[1] if len(args) > 1 else Prompt.ask("Enter backup name")

            if Confirm.ask(f"🔄 Restore from backup '{backup_name}'?"):
                # TODO: Implement backup restore
                self.console.print("✅ Backup restored (not implemented yet)", style="green")

        else:
            self.console.print("Usage: backup [create|restore|list]", style="yellow")

    def do_clear(self, arg):
        """Clear the screen"""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')

    def do_version(self, arg):
        """Show PyDock version"""
        from . import __version__

        panel = Panel(
            f"PyDock version {__version__}\n"
            f"Python Docker Deployment Manager\n"
            f"Environment: {self.settings.environment}",
            title="📦 Version Info",
            border_style="blue"
        )
        self.console.print(panel)

    def do_help(self, arg):
        """Show help information"""
        if arg:
            # Show help for specific command
            super().do_help(arg)
        else:
            # Show custom help menu
            help_text = """
🐳 PyDock Interactive Shell Commands:

📋 Project Management:
  init          - Initialize new project
  status        - Show project status
  config        - View/edit configuration
  deploy        - Deploy to VPS
  stop          - Stop all services
  logs          - View application logs

🌐 DNS & Cloudflare:
  cloudflare    - Cloudflare DNS management

📂 Git Operations:
  git           - Git repository operations

🔧 Development:
  generate      - Generate sample applications
  env           - Environment variable management
  server        - Start/stop API server

💾 Backup:
  backup        - Backup management

🛠️  Utilities:
  clear         - Clear screen
  version       - Show version
  help          - Show this help
  exit/quit     - Exit shell

Type 'help <command>' for detailed help on any command.
"""

            panel = Panel(help_text, title="🆘 Help", border_style="blue")
            self.console.print(panel)

    def do_exit(self, arg):
        """Exit the shell"""
        self.console.print("👋 Goodbye!", style="cyan")
        return True

    def do_quit(self, arg):
        """Exit the shell"""
        return self.do_exit(arg)

    def do_EOF(self, arg):
        """Handle Ctrl+D"""
        self.console.print("\n👋 Goodbye!", style="cyan")
        return True

    def emptyline(self):
        """Handle empty line"""
        pass

    def default(self, line):
        """Handle unknown commands"""
        self.console.print(f"❌ Unknown command: {line}", style="red")
        self.console.print("Type 'help' for available commands", style="yellow")

    def cmdloop(self, intro=None):
        """Override cmdloop to handle keyboard interrupts"""
        try:
            super().cmdloop(intro)
        except KeyboardInterrupt:
            self.console.print("\n⚠️  Use 'exit' or 'quit' to leave", style="yellow")
            self.cmdloop()


def interactive_shell():
    """Start the interactive PyDock shell"""
    shell = PyDockShell()
    shell.cmdloop()


if __name__ == "__main__":
    interactive_shell()
    Error
    getting
    status: {e}
    ", style="
    red
    ")


    def do_init(self, arg):
        """Initialize new PyDock project
        Usage: init [domain] [vps_ip] [ssh_key_path]
        """
        args = arg.split() if arg else []

        # Get domain
        if len(args) > 0:
            domain = args[0]
        else:
            domain = Prompt.ask("🌐 Enter domain name")

        # Get VPS IP
        if len(args) > 1:
            vps_ip = args[1]
        else:
            vps_ip = Prompt.ask("🖥️  Enter VPS IP address")

        # Get SSH key path
        if len(args) > 2:
            ssh_key_path = args[2]
        else:
            ssh_key_path = Prompt.ask("🔑 Enter SSH key path", default="~/.ssh/id_rsa")

        try:
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
            ) as progress:
                task = progress.add_task("Initializing project...", total=None)

                self.manager = PyDockManager()
                self.manager.init_project(domain, vps_ip, ssh_key_path)
                self.current_project = domain
                self._update_prompt()

                progress.update(task, description="✅ Project initialized!")

            self.console.print(f"🎉 Project initialized for domain: {domain}", style="green")

        except Exception as e:
            self.console.print(f"❌ Initialization failed: {e}", style="red")


    def do_deploy(self, arg):
        """Deploy project to VPS
        Usage: deploy [environment]
        """
        if not self.manager:
            self.console.print("❌ No project loaded. Use 'init' first.", style="red")
            return

        environment = arg.strip() or "production"

        if not Confirm.ask(f"🚀 Deploy to {environment}?"):
            self.console.print("❌ Deployment cancelled", style="yellow")
            return

        try:
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
            ) as progress:
                task = progress.add_task("Deploying...", total=None)

                progress.update(task, description="🔌 Testing VPS connection...")
                progress.update(task, description="🌐 Checking DNS...")
                progress.update(task, description="📁 Uploading files...")
                progress.update(task, description="🐳 Starting containers...")

                self.manager.deploy(environment)

                progress.update(task, description="✅ Deployment completed!")

            config = self.manager.config.load()
            domain = config.get("domain")

            self.console.print("🎉 Deployment successful!", style="green")
            self.console.print(f"🌐 Your app is available at: https://{domain}", style="cyan")

        except Exception as e:
            self.console.print(f"❌ Deployment failed: {e}", style="red")


    def do_logs(self, arg):
        """Show application logs
        Usage: logs [service] [--follow]
        """
        if not self.manager:
            self.console.print("❌ No project loaded", style="red")
            return

        args = arg.split()
        service = args[0] if args else None
        follow = "--follow" in args or "-f" in args

        try:
            self.manager.logs(service, follow)
        except Exception as e:
            self.console.print(f"❌ Failed to get logs: {e}", style="red")


    def do_stop(self, arg):
        """Stop all services"""
        if not self.manager:
            self.console.print("❌ No project loaded", style="red")
            return

        if not Confirm.ask("🛑 Stop all services?"):
            return

        try:
            self.manager.stop()
            self.console.print("✅ Services stopped", style="green")
        except Exception as e:
            self.console.print(f"❌ Failed to stop services: {e}", style="red")


    def do_config(self, arg):
        """Show or edit configuration
        Usage: config [show|edit|set key value]
        """
        if not self.manager:
            self.console.print("❌ No project loaded", style="red")
            return

        args = arg.split()
        command = args[0] if args else "show"

        if command == "show":
            try:
                config = self.manager.config.load()

                # Pretty print JSON
                syntax = Syntax(
                    json.dumps(config, indent=2),
                    "json",
                    theme="monokai",
                    line_numbers=True
                )

                panel = Panel(syntax, title="📋 Configuration", border_style="blue")
                self.console.print(panel)

            except Exception as e:
                self.console.print(f"❌ Failed to load config: {e}", style="red")

        elif command == "edit":
            self.console.print("📝 Opening config in editor...", style="cyan")
            import os
            os.system("${EDITOR:-nano} pydock.json")

        elif command == "set" and len(args) >= 3:
            key = args[1]
            value = " ".join(args[2:])

            try:
                # Try to parse as JSON if possible
                try:
                    value = json.loads(value)
                except:
                    pass

                self.manager.config.update({key: value})
                self.console.print(f"✅ Set {key} = {value}", style="green")

            except Exception as e:
                self.console.print(f"❌ Failed to set config: {e}", style="red")

        else:
            self.console.print("Usage: config [show|edit|set key value]", style="yellow")


    def do_cloudflare(self, arg):
        """Cloudflare DNS management
        Usage: cloudflare [setup|zones|records] [options]
        """
        args = arg.split()
        if not args:
            self.console.print("Usage: cloudflare [setup|zones|records]", style="yellow")
            return

        command = args[0]

        # Get Cloudflare token
        cf_token = self.settings.cloudflare_api_token
        if not cf_token:
            cf_token = Prompt.ask("🔑 Enter Cloudflare API token")

        try:
            cf_manager = CloudflareManager(cf_token)

            if command == "zones":
                asyncio.run(self._cloudflare_zones(cf_manager))
            elif command == "setup":
                asyncio.run(self._cloudflare_setup(cf_manager))
            elif command == "records":
                domain = args[1] if len(args) > 1 else Prompt.ask("🌐 Enter domain")
                asyncio.run(self._cloudflare_records(cf_manager, domain))
            else:
                self.console.print("Unknown cloudflare command", style="red")

        except Exception as e:
            self.console.print(f"❌ Cloudflare error: {e}", style="red")


    async def _cloudflare_zones(self, cf_manager):
        """List Cloudflare zones"""
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

        self.console.print(table)


    async def _cloudflare_setup(self, cf_manager):
        """Setup Cloudflare DNS"""
        if not self.manager:
            self.console.print("❌ No project loaded", style="red")
            return

        config = self.manager.config.load()
        domain = config.get("domain")
        vps_ip = config.get("vps_ip")

        if not domain or not vps_ip:
            self.console.print("❌ Domain or VPS IP not configured", style="red")
            return

        records = await cf_manager.setup_dns_records(domain, vps_ip)

        self.console.print(f"✅ Configured {len(records)} DNS records", style="green")


    async def _cloudflare_records(self, cf_manager, domain):
        """List DNS records for domain"""
        zone = await cf_manager.get_zone_by_domain(domain)
        if not zone:
            self.console.print(f"❌ Zone not found for {domain}", style="red")
            return

        records = await cf_manager.list_dns_records(zone["id"])

        table = Table(title=f"📋 DNS Records for {domain}")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Content", style="yellow")
        table.add_column("Proxied", style="magenta")

        for record in records:
            proxied = "✅" if record.get("proxied") else "❌"
            table.add_row(
                record.get("name", ""),
                record.get("type", ""),
                record.get("content", ""),
                proxied
            )

        self.console.print(table)


    def do_git(self, arg):
        """Git operations
        Usage: git [info|validate|status]
        """
        args = arg.split()
        command = args[0] if args else "info"

        if command == "info":
            info = get_repo_info(".")
            if info:
                table = Table(title="📂 Git Repository Info")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")

                for key, value in info.items():
                    if isinstance(value, list):
                        value = ", ".join(value) if value else "None"
                    elif isinstance(value, bool):
                        value = "✅" if value else "❌"

                    table.add_row(str(key).replace("_", " ").title(), str(value))

                self.console.print(table)
            else:
                self.console.print("❌ Not a Git repository", style="red")

        elif command == "validate":
            validation = validate_repo_for_deployment(".")

            # Show validation results
            if validation["valid"]:
                self.console.print("✅ Repository is ready for deployment", style="green")
            else:
                self.console.print("❌ Repository has issues", style="red")

            # Show errors
            if validation["errors"]:
                error_panel = Panel(
                    "\n".join(f"• {error}" for error in validation["errors"]),
                    title="❌ Errors",
                    border_style="red"
                )
                self.console.print(error_panel)

            # Show warnings
            if validation["warnings"]:
                warning_panel = Panel(
                    "\n".join(f"• {warning}" for warning in validation["warnings"]),
                    title="⚠️  Warnings",
                    border_style="yellow"
                )
                self.console.print(warning_panel)

            # Show recommendations
            if validation["recommendations"]:
                rec_panel = Panel(
                    "\n".join(f"• {rec}" for rec in validation["recommendations"]),
                    title="💡 Recommendations",
                    border_style="blue"
                )
                self.console.print(rec_panel)

        else:
            self.console.print("Usage: git [info|validate|status]", style="yellow")


    def do_generate(self, arg):
        """Generate sample applications
        Usage: generate [app|static|api]
        """
        if not arg:
            self.console.print("Usage: generate [app|static|api]", style="yellow")
            return

        from .generators import generate_sample_app

        try:
            generate_sample_app(arg)
            self.console.print(f"✅ Generated {arg} application", style="green")
        except Exception as e:
            self.console.print(f"❌