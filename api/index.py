"""
Vercel serverless function entry point for Django application.
"""
import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wesolucions.settings')

# Import Django and setup
import django
django.setup()

# Import WSGI application
from wesolucions.wsgi import application

# Vercel serverless function handler (standard format)
def handler(request):
    """Handle incoming requests for Vercel."""
    from io import BytesIO
    
    # Extract path from request
    path = request.path if hasattr(request, 'path') else '/'
    if path.startswith('/api'):
        path = path[4:] if len(path) > 4 else '/'
    
    # Build WSGI environ
    environ = {
        'REQUEST_METHOD': request.method if hasattr(request, 'method') else 'GET',
        'PATH_INFO': path,
        'SCRIPT_NAME': '',
        'QUERY_STRING': '',
        'CONTENT_TYPE': request.headers.get('content-type', '') if hasattr(request, 'headers') else '',
        'CONTENT_LENGTH': '0',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': BytesIO(),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add headers if available
    if hasattr(request, 'headers'):
        for key, value in request.headers.items():
            key = key.upper().replace('-', '_')
            if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key}'] = value
    
    # Handle request body
    if hasattr(request, 'body') and request.body:
        environ['CONTENT_LENGTH'] = str(len(request.body))
        environ['wsgi.input'] = BytesIO(request.body)
    
    # Handle query string
    if hasattr(request, 'query_string') and request.query_string:
        environ['QUERY_STRING'] = request.query_string.decode() if isinstance(request.query_string, bytes) else request.query_string
    
    # Call WSGI application
    response_data = {'status': None, 'headers': []}
    
    def start_response(status, headers):
        response_data['status'] = status
        response_data['headers'] = headers
    
    try:
        result = application(environ, start_response)
        body = b''.join(result)
        
        # Parse status code
        status_code = int(response_data['status'].split()[0]) if response_data['status'] else 200
        
        # Convert headers to dict
        headers_dict = {k: v for k, v in response_data['headers']}
        
        return {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': body.decode('utf-8', errors='ignore')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "{str(e)}"}}'
        }

