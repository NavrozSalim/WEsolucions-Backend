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
    from urllib.parse import parse_qs
    
    try:
        # Get path from request
        path = getattr(request, 'path', '/')
        
        # Get query string
        query_string = ''
        if hasattr(request, 'query_string'):
            query_string = request.query_string
            if isinstance(query_string, bytes):
                query_string = query_string.decode('utf-8')
        
        # Get request body
        body = b''
        if hasattr(request, 'body'):
            body = request.body if isinstance(request.body, bytes) else request.body.encode()
        
        # Get method
        method = getattr(request, 'method', 'GET')
        
        # Get headers
        headers = {}
        if hasattr(request, 'headers'):
            headers = dict(request.headers)
        
        # Build WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'SCRIPT_NAME': '',
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', headers.get('Content-Type', '')),
            'CONTENT_LENGTH': str(len(body)),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(body),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        
        # Add HTTP headers
        for key, value in headers.items():
            key_upper = key.upper().replace('-', '_')
            if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                environ[f'HTTP_{key_upper}'] = value
        
        # Call WSGI application
        response_data = {'status': None, 'headers': []}
        
        def start_response(status, headers_list):
            response_data['status'] = status
            response_data['headers'] = headers_list
        
        result = application(environ, start_response)
        
        # Collect response body
        body_parts = []
        for part in result:
            if isinstance(part, bytes):
                body_parts.append(part)
            else:
                body_parts.append(part.encode('utf-8'))
        
        response_body = b''.join(body_parts)
        
        # Parse status code
        status_code = 200
        if response_data['status']:
            status_code = int(response_data['status'].split()[0])
        
        # Convert headers to dict
        headers_dict = {}
        for key, value in response_data['headers']:
            headers_dict[key] = value
        
        return {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': response_body.decode('utf-8', errors='ignore')
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in handler: {e}", file=sys.stderr)
        print(error_trace, file=sys.stderr)
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Internal server error", "message": "{str(e)}"}}'
        }

