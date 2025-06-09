# Caddy Static Website Demo

This project demonstrates a simple static website served by Caddy using a Caddyfile for configuration.

## Features

- Static file serving
- Automatic HTTPS with local certificates
- HTTP/2 enabled
- Security headers
- Gzip compression

## Prerequisites

- Docker and Docker Compose
- mkcert (for local certificates)

## Quick Start

1. Generate local certificates:
   ```bash
   make certs
   ```

2. Start the services:
   ```bash
   make up
   ```

3. Open in your browser: [https://localhost](https://localhost)

## Available Commands

- `make up` - Start all services in detached mode
- `make down` - Stop and remove all containers
- `make logs` - View container logs
- `make restart` - Restart all services
- `make certs` - Generate SSL certificates
- `make clean` - Remove containers and volumes

## Project Structure

```
.
├── Caddyfile          # Caddy configuration
├── docker-compose.yml  # Docker Compose configuration
├── html/              # Static website files
│   └── index.html
├── certs/             # SSL certificates (generated)
└── Makefile           # Project commands
```

## Customization

- Edit `html/index.html` to modify the website content
- Update `Caddyfile` for custom routing or headers
- Add more static files to the `html/` directory

## Troubleshooting

- **Certificate warnings**: Make sure to install the local CA:
  ```bash
  mkcert -install
  ```
- **Port conflicts**: Stop other services using ports 80/443 or update `docker-compose.yml`

## License

Apache 2
