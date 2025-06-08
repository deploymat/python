from pathlib import Path
from .utils import FileUtils


def generate_sample_app(app_type: str):
    """
    Generuje przykładową aplikację

    Args:
        app_type: Typ aplikacji (flask, fastapi, static)
    """
    if app_type == 'flask':
        _generate_flask_app()
    elif app_type == 'fastapi':
        _generate_fastapi_app()
    elif app_type == 'static':
        _generate_static_site()


def _generate_flask_app():
    """Generuje przykładową aplikację Flask"""

    structure = {
        'web-app': {
            'app.py': '''from flask import Flask, jsonify, render_template_string
import psycopg2
import os

app = Flask(__name__)

# Template HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PyDock Flask App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; }
        .status { padding: 20px; margin: 20px 0; border-radius: 5px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .api-section { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">🐳 PyDock Flask Application</h1>
        <p>Aplikacja została pomyślnie wdrożona przez PyDock!</p>

        <div class="api-section">
            <h3>🔌 Dostępne endpointy API:</h3>
            <ul>
                <li><a href="/api/status">GET /api/status</a> - Status aplikacji</li>
                <li><a href="/api/health">GET /api/health</a> - Health check</li>
                <li><a href="/api/db">GET /api/db</a> - Test połączenia z bazą</li>
            </ul>
        </div>

        <div class="status success">
            ✅ Aplikacja działa poprawnie na porcie 5000
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def status():
    return jsonify({
        'service': 'flask-app',
        'status': 'running',
        'port': 5000,
        'deployed_by': 'PyDock',
        'environment': os.getenv('FLASK_ENV', 'development')
    })

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': __import__('datetime').datetime.now().isoformat()})

@app.route('/api/db')
def test_db():
    try:
        database_url = os.getenv('DATABASE_URL', 'postgresql://admin:password123@database:5432/myapp')

        # Parse DATABASE_URL
        if database_url.startswith('postgresql://'):
            parts = database_url.replace('postgresql://', '').split('@')
            user_pass = parts[0].split(':')
            host_db = parts[1].split('/')

            conn = psycopg2.connect(
                host=host_db[0].split(':')[0],
                port=host_db[0].split(':')[1] if ':' in host_db[0] else 5432,
                database=host_db[1],
                user=user_pass[0],
                password=user_pass[1]
            )

            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()

            return jsonify({
                'database': 'connected',
                'postgres_version': version[0] if version else 'unknown'
            })
        else:
            return jsonify({'database': 'error', 'message': 'Invalid DATABASE_URL format'})

    except Exception as e:
        return jsonify({'database': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
''',
            'requirements.txt': '''Flask==2.3.3
psycopg2-binary==2.9.7
gunicorn==21.2.0
''',
            'Dockerfile': '''FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

# Use gunicorn in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
'''
        }
    }

    FileUtils.create_directory_structure('.', structure)


def _generate_fastapi_app():
    """Generuje przykładową aplikację FastAPI"""

    structure = {
        'web-app': {
            'main.py': '''from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import psycopg2
import os
from datetime import datetime

app = FastAPI(title="PyDock FastAPI", description="API wdrożone przez PyDock")

HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>PyDock FastAPI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        .header { text-align: center; color: #333; }
        .api-section { margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">⚡ PyDock FastAPI Application</h1>
        <p>Szybkie API wdrożone przez PyDock!</p>

        <div class="api-section">
            <h3>📖 Dokumentacja API:</h3>
            <ul>
                <li><a href="/docs">Swagger UI</a></li>
                <li><a href="/redoc">ReDoc</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return HTML_CONTENT

@app.get("/api/status")
async def get_status():
    return {
        "service": "fastapi-app",
        "status": "running",
        "port": 5000,
        "deployed_by": "PyDock",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/db")
async def test_database():
    try:
        database_url = os.getenv('DATABASE_URL', 'postgresql://admin:password123@database:5432/myapp')

        if database_url.startswith('postgresql://'):
            parts = database_url.replace('postgresql://', '').split('@')
            user_pass = parts[0].split(':')
            host_db = parts[1].split('/')

            conn = psycopg2.connect(
                host=host_db[0].split(':')[0],
                port=host_db[0].split(':')[1] if ':' in host_db[0] else 5432,
                database=host_db[1],
                user=user_pass[0],
                password=user_pass[1]
            )

            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()

            return {
                "database": "connected",
                "postgres_version": version[0] if version else "unknown"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
''',
            'requirements.txt': '''fastapi==0.104.1
uvicorn==0.24.0
psycopg2-binary==2.9.7
''',
            'Dockerfile': '''FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 5000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
'''
        }
    }

    FileUtils.create_directory_structure('.', structure)


def _generate_static_site():
    """Generuje przykładową stronę statyczną"""

    structure = {
        'static-site': {
            'index.html': '''<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyDock Static Site</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 60px 0;
            color: white;
        }

        .header h1 {
            font-size: 3.5rem;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .main-content {
            background: white;
            border-radius: 15px;
            padding: 40px;
            margin: 40px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }

        .service-card {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease;
        }

        .service-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .service-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }

        .service-card p {
            margin-bottom: 15px;
            color: #666;
        }

        .btn {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s ease;
        }

        .btn:hover {
            background: #5a67d8;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #10b981;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .footer {
            text-align: center;
            padding: 40px 0;
            color: white;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🐳 PyDock Site</h1>
            <p>Strona statyczna wdrożona automatycznie przez PyDock</p>
        </header>

        <main class="main-content">
            <h2>🚀 Witaj w PyDock!</h2>
            <p>Ta strona została automatycznie wdrożona na Twój VPS przy użyciu systemu PyDock. Wszystkie usługi działają w kontenerach Docker z automatycznym SSL.</p>

            <div class="services-grid">
                <div class="service-card">
                    <h3><span class="status-indicator"></span>Web Application</h3>
                    <p>Główna aplikacja (Flask/FastAPI) z API i interfejsem użytkownika.</p>
                    <a href="/api/status" class="btn">Sprawdź API</a>
                </div>

                <div class="service-card">
                    <h3><span class="status-indicator"></span>Static Site</h3>
                    <p>Strona statyczna serwowana przez Nginx z wysoką wydajnością.</p>
                    <a href="#" class="btn">Ta strona</a>
                </div>

                <div class="service-card">
                    <h3><span class="status-indicator"></span>Database</h3>
                    <p>PostgreSQL database działająca wewnętrznie w sieci Docker.</p>
                    <a href="/api/db" class="btn">Test połączenia</a>
                </div>
            </div>

            <h3>📋 Informacje o deploymencie:</h3>
            <ul style="margin: 20px 0; padding-left: 20px;">
                <li>✅ Automatyczne SSL certyfikaty (Let's Encrypt)</li>
                <li>✅ Reverse proxy z Caddy</li>
                <li>✅ Izolacja kontenerów Docker</li>
                <li>✅ Automatyczne restarty usług</li>
                <li>✅ Backup i monitoring</li>
            </ul>

            <div style="background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4>🛠️ Zarządzanie przez PyDock:</h4>
                <code style="background: #fff; padding: 4px 8px; border-radius: 4px;">pydock status</code> - Status usług<br>
                <code style="background: #fff; padding: 4px 8px; border-radius: 4px;">pydock logs</code> - Sprawdź logi<br>
                <code style="background: #fff; padding: 4px 8px; border-radius: 4px;">pydock deploy</code> - Aktualizuj aplikację
            </div>
        </main>

        <footer class="footer">
            <p>Wdrożone przez PyDock - Python Docker Deployment Manager</p>
        </footer>
    </div>

    <script>
        // Proste sprawdzenie statusu API
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                console.log('API Status:', data);
                // Można dodać dynamiczne aktualizacje statusu
            })
            .catch(error => {
                console.log('API niedostępne:', error);
            });
    </script>
</body>
</html>''',
            'about.html': '''<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>O PyDock</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>📖 O PyDock</h1>
            <p>Python Docker Deployment Manager</p>
        </header>

        <main class="main-content">
            <h2>Czym jest PyDock?</h2>
            <p>PyDock to narzędzie do automatycznego wdrażania aplikacji Docker na VPS bez modyfikacji środowiska lokalnego.</p>

            <h3>Główne funkcje:</h3>
            <ul>
                <li>🚀 Jednokomendowy deployment na VPS</li>
                <li>🔒 Automatyczne SSL certyfikaty</li>
                <li>🐳 Zarządzanie kontenerami Docker</li>
                <li>🌐 Reverse proxy z Caddy</li>
                <li>📊 Monitoring i logi</li>
            </ul>

            <a href="/" class="btn">Powrót</a>
        </main>
    </div>
</body>
</html>''',
            'style.css': '''/* Współdzielony CSS dla dodatkowych stron */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.header {
    text-align: center;
    padding: 60px 0;
    color: white;
}

.header h1 {
    font-size: 3.5rem;
    margin-bottom: 20px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.main-content {
    background: white;
    border-radius: 15px;
    padding: 40px;
    margin: 40px 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.btn {
    display: inline-block;
    background: #667eea;
    color: white;
    padding: 12px 24px;
    text-decoration: none;
    border-radius: 5px;
    transition: background 0.3s ease;
}

.btn:hover {
    background: #5a67d8;
}'''
        }
    }

    FileUtils.create_directory_structure('.', structure)