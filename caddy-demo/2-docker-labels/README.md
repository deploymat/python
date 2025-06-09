# Caddy Docker Proxy Demo

This project demonstrates how to use Docker labels to dynamically configure Caddy as a reverse proxy for multiple services.

## Features

- Automatic service discovery
- Dynamic reverse proxy configuration
- Multiple services with automatic HTTPS
- Global middleware support
- Health checks

## Prerequisites

- Docker and Docker Compose
- sudo access (for modifying /etc/hosts)

## Quick Start

1. Run the setup script (requires sudo):
   ```bash
   sudo make setup
   ```

2. Start the services:
   ```bash
   make up
   ```

3. Access the services:
   - Web: [https://web.demo.local](https://web.demo.local)
   - API: [https://api.demo.local](https://api.demo.local)

## Available Commands

- `make up` - Start all services in detached mode
- `make down` - Stop and remove all containers
- `make logs` - View container logs
- `make restart` - Restart all services
- `make setup` - Initial setup (modifies /etc/hosts)
- `make clean` - Remove containers, networks, and volumes

## Project Structure

```
.
├── docker-compose.yml  # Docker Compose configuration
├── api/                # Python API service
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── web/               # Static web files
│   └── index.html
└── Makefile           # Project commands
```

## Adding New Services

To add a new service, add it to `docker-compose.yml` with the appropriate labels:

```yaml
services:
  my-service:
    image: nginx:alpine
    labels:
      - caddy=myservice.demo.local
      - caddy.reverse_proxy={{upstreams 80}}
      - caddy.@default  # Apply global middleware
    networks:
      - caddy_network
```

## Troubleshooting

### Certificate Warnings
For local development, you'll need to accept the self-signed certificate in your browser.

### Hosts File
If you can't access the services:
1. Verify the entries in `/etc/hosts`:
   ```
   127.0.0.1 web.demo.local api.demo.local
   ```
2. Make sure you ran `sudo make setup`

### Port Conflicts
If ports 80/443 are in use:
1. Stop other web servers
2. Or update the port mappings in `docker-compose.yml`

## License

Apache 2
