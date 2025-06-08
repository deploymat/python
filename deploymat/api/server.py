from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
import logging
from datetime import datetime
import uuid

from ..settings import get_settings
from ..core import PyDockManager
from ..utils import Logger
from ..cloudflare import CloudflareManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="PyDock API",
    description="Python Docker Deployment Manager REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Security
security = HTTPBearer(auto_error=False)

# Global state
deployment_tasks: Dict[str, Dict] = {}
websocket_connections: List[WebSocket] = []


# Pydantic Models
class DeploymentRequest(BaseModel):
    """Request model for deployment"""
    domain: str = Field(..., description="Domain name (e.g., example.com)")
    vps_ip: str = Field(..., description="VPS IP address")
    cf_token: Optional[str] = Field(None, description="Cloudflare API token")
    source: Optional[str] = Field(None, description="Git repository URL")
    ssh_key_path: Optional[str] = Field(None, description="SSH key path")
    environment: str = Field(default="production", description="Environment name")
    auto_dns: bool = Field(default=True, description="Auto-configure DNS")
    services: Optional[Dict[str, Any]] = Field(None, description="Custom services configuration")


class DeploymentResponse(BaseModel):
    """Response model for deployment"""
    deployment_id: str
    status: str
    message: str
    domain: str
    created_at: datetime


class ProjectRequest(BaseModel):
    """Request model for project initialization"""
    domain: str
    vps_ip: str
    ssh_key_path: Optional[str] = None
    project_name: Optional[str] = None


class StatusResponse(BaseModel):
    """Response model for status"""
    status: str
    services: List[Dict[str, Any]]
    uptime: Optional[str] = None
    last_deployment: Optional[datetime] = None


class LogsRequest(BaseModel):
    """Request model for logs"""
    service: Optional[str] = None
    lines: int = Field(default=100, ge=1, le=10000)
    follow: bool = Field(default=False)


# Authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token authentication"""
    if not credentials:
        return None

    # In production, implement proper JWT validation
    if credentials.credentials == settings.api_secret_key:
        return {"username": "api_user"}

    return None


async def require_auth(current_user=Depends(get_current_user)):
    """Require authentication"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user


# Utility functions
async def broadcast_to_websockets(message: Dict):
    """Broadcast message to all connected websockets"""
    if not websocket_connections:
        return

    message_str = json.dumps(message)
    disconnected = []

    for websocket in websocket_connections:
        try:
            await websocket.send_text(message_str)
        except:
            disconnected.append(websocket)

    # Remove disconnected websockets
    for ws in disconnected:
        websocket_connections.remove(ws)


async def run_deployment_task(deployment_id: str, request: DeploymentRequest):
    """Background task for deployment"""
    try:
        # Update status
        deployment_tasks[deployment_id]["status"] = "running"
        await broadcast_to_websockets({
            "type": "deployment_status",
            "deployment_id": deployment_id,
            "status": "running",
            "message": "Starting deployment..."
        })

        # Initialize PyDock manager
        manager = PyDockManager(f"deployment-{deployment_id}.json")

        # Initialize project
        manager.init_project(
            domain=request.domain,
            vps_ip=request.vps_ip,
            ssh_key_path=request.ssh_key_path
        )

        # Configure Cloudflare DNS if token provided
        if request.cf_token and request.auto_dns:
            cf_manager = CloudflareManager(request.cf_token)
            await cf_manager.setup_dns_records(request.domain, request.vps_ip)

            await broadcast_to_websockets({
                "type": "deployment_log",
                "deployment_id": deployment_id,
                "message": "✅ DNS records configured"
            })

        # Clone source if provided
        if request.source:
            from ..git import clone_git_repo
            clone_git_repo(request.source, f"./deployments/{deployment_id}")

            await broadcast_to_websockets({
                "type": "deployment_log",
                "deployment_id": deployment_id,
                "message": f"✅ Source cloned from {request.source}"
            })

        # Deploy to VPS
        await broadcast_to_websockets({
            "type": "deployment_log",
            "deployment_id": deployment_id,
            "message": "🚀 Deploying to VPS..."
        })

        manager.deploy(request.environment)

        # Update status
        deployment_tasks[deployment_id]["status"] = "completed"
        deployment_tasks[deployment_id]["completed_at"] = datetime.now()

        await broadcast_to_websockets({
            "type": "deployment_status",
            "deployment_id": deployment_id,
            "status": "completed",
            "message": f"🎉 Deployment completed! Available at https://{request.domain}"
        })

    except Exception as e:
        deployment_tasks[deployment_id]["status"] = "failed"
        deployment_tasks[deployment_id]["error"] = str(e)

        await broadcast_to_websockets({
            "type": "deployment_status",
            "deployment_id": deployment_id,
            "status": "failed",
            "message": f"❌ Deployment failed: {str(e)}"
        })


# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "PyDock API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/deploy", response_model=DeploymentResponse)
async def create_deployment(
        request: DeploymentRequest,
        background_tasks: BackgroundTasks,
        current_user=Depends(require_auth)
):
    """Create new deployment"""
    deployment_id = str(uuid.uuid4())

    # Store deployment task
    deployment_tasks[deployment_id] = {
        "id": deployment_id,
        "status": "queued",
        "domain": request.domain,
        "created_at": datetime.now(),
        "request": request.dict()
    }

    # Start background deployment
    background_tasks.add_task(run_deployment_task, deployment_id, request)

    return DeploymentResponse(
        deployment_id=deployment_id,
        status="queued",
        message="Deployment queued successfully",
        domain=request.domain,
        created_at=datetime.now()
    )


@app.get("/deployments")
async def list_deployments(current_user=Depends(require_auth)):
    """List all deployments"""
    return {
        "deployments": list(deployment_tasks.values()),
        "total": len(deployment_tasks)
    }


@app.get("/deployments/{deployment_id}")
async def get_deployment(deployment_id: str, current_user=Depends(require_auth)):
    """Get deployment details"""
    if deployment_id not in deployment_tasks:
        raise HTTPException(status_code=404, detail="Deployment not found")

    return deployment_tasks[deployment_id]


@app.delete("/deployments/{deployment_id}")
async def cancel_deployment(deployment_id: str, current_user=Depends(require_auth)):
    """Cancel deployment"""
    if deployment_id not in deployment_tasks:
        raise HTTPException(status_code=404, detail="Deployment not found")

    task = deployment_tasks[deployment_id]
    if task["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed deployment")

    task["status"] = "cancelled"
    task["cancelled_at"] = datetime.now()

    return {"message": "Deployment cancelled", "deployment_id": deployment_id}


@app.post("/projects/init")
async def init_project(request: ProjectRequest, current_user=Depends(require_auth)):
    """Initialize new project"""
    try:
        manager = PyDockManager()
        manager.init_project(
            domain=request.domain,
            vps_ip=request.vps_ip,
            ssh_key_path=request.ssh_key_path
        )

        return {
            "message": "Project initialized successfully",
            "domain": request.domain,
            "vps_ip": request.vps_ip
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/projects/status")
async def get_project_status(current_user=Depends(require_auth)):
    """Get project status"""
    try:
        manager = PyDockManager()

        if not manager.config.exists():
            raise HTTPException(status_code=404, detail="No project configured")

        config = manager.config.load()

        # TODO: Get actual service status from VPS
        services = [
            {"name": service, "status": "running", "port": config["services"][service].get("port")}
            for service in config["services"]
        ]

        return StatusResponse(
            status="running",
            services=services,
            last_deployment=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/logs")
async def get_logs(request: LogsRequest, current_user=Depends(require_auth)):
    """Get application logs"""
    try:
        manager = PyDockManager()

        if not manager.config.exists():
            raise HTTPException(status_code=404, detail="No project configured")

        # TODO: Implement actual log retrieval from VPS
        logs = [
            f"[{datetime.now().isoformat()}] INFO: Service {request.service or 'all'} log entry {i}"
            for i in range(min(request.lines, 100))
        ]

        return {"logs": logs, "service": request.service, "lines": len(logs)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/stop")
async def stop_project(current_user=Depends(require_auth)):
    """Stop project services"""
    try:
        manager = PyDockManager()
        manager.stop()

        return {"message": "Project stopped successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/cloudflare/dns")
async def setup_dns(
        domain: str,
        vps_ip: str,
        cf_token: str,
        current_user=Depends(require_auth)
):
    """Setup Cloudflare DNS records"""
    try:
        cf_manager = CloudflareManager(cf_token)
        records = await cf_manager.setup_dns_records(domain, vps_ip)

        return {
            "message": "DNS records configured successfully",
            "domain": domain,
            "records": records
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/cloudflare/zones")
async def list_zones(cf_token: str, current_user=Depends(require_auth)):
    """List Cloudflare zones"""
    try:
        cf_manager = CloudflareManager(cf_token)
        zones = await cf_manager.list_zones()

        return {"zones": zones}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected to PyDock API",
            "timestamp": datetime.now().isoformat()
        }))

        # Keep connection alive
        while True:
            try:
                # Wait for client messages (ping/pong)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)

                # Echo back for ping/pong
                if data == "ping":
                    await websocket.send_text("pong")

            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_text(json.dumps({
                    "type": "keepalive",
                    "timestamp": datetime.now().isoformat()
                }))

    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)


@app.get("/logs/stream")
async def stream_logs(
        service: Optional[str] = None,
        follow: bool = False,
        current_user=Depends(require_auth)
):
    """Stream logs in real-time"""

    async def generate_logs():
        """Generate log stream"""
        try:
            # TODO: Implement actual log streaming from VPS
            for i in range(100):
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "service": service or "system",
                    "level": "INFO",
                    "message": f"Log entry {i} from {service or 'system'}"
                }

                yield f"data: {json.dumps(log_entry)}\n\n"

                if not follow:
                    break

                await asyncio.sleep(1)

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_logs(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )


@app.get("/metrics")
async def get_metrics(current_user=Depends(require_auth)):
    """Get deployment metrics"""
    return {
        "deployments": {
            "total": len(deployment_tasks),
            "running": len([t for t in deployment_tasks.values() if t["status"] == "running"]),
            "completed": len([t for t in deployment_tasks.values() if t["status"] == "completed"]),
            "failed": len([t for t in deployment_tasks.values() if t["status"] == "failed"])
        },
        "system": {
            "websocket_connections": len(websocket_connections),
            "uptime": "Unknown",  # TODO: Calculate actual uptime
            "memory_usage": "Unknown"  # TODO: Get actual memory usage
        }
    }


@app.post("/git/validate")
async def validate_git_url(url: str, current_user=Depends(require_auth)):
    """Validate Git repository URL"""
    try:
        from ..git import is_valid_git_url

        is_valid = is_valid_git_url(url)

        return {
            "url": url,
            "valid": is_valid,
            "message": "Valid Git repository" if is_valid else "Invalid Git repository"
        }

    except Exception as e:
        return {"url": url, "valid": False, "message": str(e)}


# Server runner
def run_server(host: str = None, port: int = None, reload: bool = None):
    """Run the PyDock API server"""
    import uvicorn

    # Use settings or provided values
    host = host or settings.api_host
    port = port or settings.api_port
    reload = reload if reload is not None else settings.api_reload

    logger.info(f"🚀 Starting PyDock API server on {host}:{port}")
    logger.info(f"📖 API Documentation: http://{host}:{port}/docs")

    uvicorn.run(
        "pydock.api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_server()