from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os

app = FastAPI(title="API Service", version="1.0.0")

# Sample data
services = [
    {"name": "User Service", "status": "online", "endpoint": "/users"},
    {"name": "Product Service", "status": "online", "endpoint": "/products"},
    {"name": "Order Service", "status": "online", "endpoint": "/orders"},
]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Service</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }
            .header {
                background: #2c3e50;
                color: white;
                padding: 1rem;
                border-radius: 5px;
                margin-bottom: 2rem;
            }
            .service {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 1rem;
                margin-bottom: 1rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .status {
                padding: 0.3rem 0.8rem;
                border-radius: 20px;
                font-size: 0.9rem;
                font-weight: bold;
            }
            .online {
                background: #2ecc71;
                color: white;
            }
            .endpoints {
                margin-top: 2rem;
            }
            .endpoint {
                background: #f8f9fa;
                padding: 0.8rem;
                border-radius: 5px;
                margin-bottom: 0.5rem;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>API Service</h1>
            <p>Welcome to the API service. This service provides various endpoints for the application.</p>
        </div>

        <h2>Service Status</h2>
        <div id="services">
            <div class="service">
                <div>
                    <h3>API Service</h3>
                    <p>Core API endpoints and functionality</p>
                </div>
                <span class="status online">ONLINE</span>
            </div>
        </div>

        <div class="endpoints">
            <h2>Available Endpoints</h2>
            <div class="endpoint">
                <strong>GET</strong> /api/status - Check API status
            </div>
            <div class="endpoint">
                <strong>GET</strong> /api/time - Get current server time
            </div>
            <div class="endpoint">
                <strong>GET</strong> /api/health - Health check endpoint
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "service": "API Service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/time")
async def get_time():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "timezone": "UTC"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
