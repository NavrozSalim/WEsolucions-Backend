"""
Netlify serverless function for Django API.
"""
import os
import sys
from pathlib import Path

# Add project to path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wesolucions.settings')
os.environ['NETLIFY'] = '1'  # Mark as Netlify environment

# Import Django
import django
django.setup()

# Suppress warnings
import warnings
warnings.filterwarnings('ignore', message='No directory at')
warnings.filterwarnings('ignore', category=UserWarning, module='django.core.handlers.base')

# Import WSGI application
from wesolucions.wsgi import application

def handler(event, context):
    """Netlify serverless function handler."""
    from io import BytesIO
    
    try:
        # Parse Netlify event
        raw_path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        body = event.get('body', '')
        query_string = event.get('queryStringParameters', {})
        
        # Handle Netlify function path - remove /.netlify/functions/api prefix if present
        # This allows rewrites from /api/* to work correctly
        if raw_path.startswith('/.netlify/functions/api'):
            path = raw_path.replace('/.netlify/functions/api', '', 1) or '/'
        elif raw_path.startswith('/api'):
            # Already has /api prefix, use as is
            path = raw_path
        else:
            # No prefix, assume it's an API call
            path = raw_path
        
        # Convert query string to string
        if query_string:
            from urllib.parse import urlencode
            query_string = urlencode(query_string)
        else:
            query_string = ''
        
        # Convert body to bytes
        if isinstance(body, str):
            body_bytes = body.encode('utf-8')
        else:
            body_bytes = body if body else b''
        
        # Build WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'SCRIPT_NAME': '',
            'QUERY_STRING': query_string,
            'CONTENT_TYPE': headers.get('content-type', headers.get('Content-Type', '')),
            'CONTENT_LENGTH': str(len(body_bytes)),
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(body_bytes),
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
        print(f"Error in Netlify handler: {e}", file=sys.stderr)
        print(error_trace, file=sys.stderr)
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "Internal server error", "message": "{str(e)}"}}'
        }

