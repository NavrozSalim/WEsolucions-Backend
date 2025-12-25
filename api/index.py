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

# Vercel serverless function handler
def handler(request):
    """Handle incoming requests for Vercel."""
    from io import BytesIO
    
    # Build WSGI environ from Vercel request
    environ = {
        'REQUEST_METHOD': request.method,
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string.decode() if request.query_string else '',
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': str(len(request.body)) if request.body else '0',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': BytesIO(request.body) if request.body else BytesIO(),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers
    for key, value in request.headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value
    
    # Call WSGI application
    response_data = {'status': None, 'headers': []}
    
    def start_response(status, headers):
        response_data['status'] = status
        response_data['headers'] = headers
    
    result = application(environ, start_response)
    
    # Collect response body
    body = b''.join(result)
    
    # Parse status code
    status_code = int(response_data['status'].split()[0])
    
    # Convert headers to dict
    headers_dict = dict(response_data['headers'])
    
    return {
        'statusCode': status_code,
        'headers': headers_dict,
        'body': body.decode('utf-8')
    }

