"""
FPC Playground Backend Server

This Flask application provides a REST API for compiling and running Free Pascal code.
It receives Pascal source code via HTTP POST requests and returns the execution results.
"""

import code
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from fpc_runner import compile_and_run
import base64
from urllib.parse import unquote
import os
import re

# Server configuration
HOST = '0.0.0.0'  # Listen on all network interfaces (allows external connections)

MAX_CODE_SIZE = 16 * 1024    # Max number of characters allowed in pascal code
MAX_OUTPUT_SIZE = 48 * 1024  # Max number of characters output
MAX_ARGS_SIZE = 64          # Max number of characters allowed in program arguments
MAX_INPUT_SIZE = 64         # Max number of characters allowed in user input

# Get backend port from environment variable or default to 5000
backend_port = os.getenv('BACKEND_PORT', '5000')

# Initialize Flask application
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["150 per hour", "10 per minute"],
    storage_uri="memory://",
)

# Enable CORS for all routes (allows frontend to call backend from different origins)
CORS(app)

# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Print startup information
print(f"Flask app initialized. Backend port: {backend_port}", flush=True)
print("Available routes:", flush=True)
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}", flush=True)


@app.route('/', methods=['GET'])
def root():
    """
    Root endpoint for testing.
    """
    return jsonify({'message': 'FPC Playground Backend is running!'}), 200


# Debugging log for /health endpoint
@app.route('/health', methods=['GET'])
def health():
    print("/health endpoint accessed", flush=True)
    """
    Health endpoint to check if the server is running.
    
    Returns a simple JSON response indicating server status.
    """
    return jsonify({'status': 'ok'}), 200

@app.errorhandler(500)
def internal_error(error):
    """
    Handle internal server errors (HTTP 500).
    
    Returns a JSON response with an error message.
    """
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_error(error):
    """
    Handle rate limit exceeded errors (HTTP 429).
    
    Returns a JSON response indicating that the rate limit has been exceeded.
    """
    return jsonify({'error': 'Rate limit exceeded'}), 429

@app.route('/run', methods=['POST'])
def run_code():
    """
    API endpoint to compile and execute Free Pascal code.
    
    Expected JSON payload:
    {
        "code": "program HelloWorld; begin writeln('Hello, World!'); end."
    }
    
    Returns JSON response:
    {
        "output": "Hello, World!\n"  // or compilation/runtime errors
    }
    """

    # Check if the request has JSON content type
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    # Check if the the request body can be parsed as JSON
    try:
        encodedCode = request.get_json(force=True).get('code', '')
        encodedArgs = request.get_json(force=True).get('args', '')
        encodedInput = request.get_json(force=True).get('input', '')
    except Exception:
        return jsonify({'error':'Invalid JSON'}), 400

    code = base64.b64decode(encodedCode).decode('utf-8')
    args = base64.b64decode(encodedArgs).decode('utf-8')
    user_input = base64.b64decode(encodedInput).decode('utf-8')

    # Check if the code exceeds the maximum allowed size
    if len(code) > MAX_CODE_SIZE:
        # Limit the size of the code to prevent usage abuse
        return jsonify({'error' : f'Code size exceeds limit of {MAX_CODE_SIZE:,} characters.'}), 400

    # Check if the program arguments exceed the maximum allowed size
    if len(args) > MAX_ARGS_SIZE:
        return jsonify({'error' : f'Program arguments size exceeds limit of {MAX_ARGS_SIZE:,} characters.'}), 400  
    
    # Check if the user input exceeds the maximum allowed size
    if len(user_input) > MAX_INPUT_SIZE:
        return jsonify({'error' : f'User input size exceeds limit of {MAX_INPUT_SIZE:,} characters.'}), 400 

    # Validate input characters to prevent encoding attacks
    if any(ord(char) < 32 or ord(char) > 126 for char in code if char not in '\n\r\t'):
        return jsonify({'error': 'Code contains invalid characters.'}), 400

    # Check for excessive nested structures that could cause compilation issues
    if code.count('begin') > 20 or code.count('(') > 100 or code.count('[') > 50:
        return jsonify({'error': 'Code structure too complex.'}), 400

    # List of dangerous Pascal procedures/functions that could compromise security
    dangerous_keywords = [
        # File system operations (prevent browsing, creating, or deleting files/folders)
        'deletefile', 'removedir', 'rename', 'rmdir', 'unlink', 'fpunlink',
        'mkdir', 'fpmkdir', 'chdir', 'fpchdir', 'chmod', 'fpchmod',
        'assign', 'rewrite', 'append', 'reset', 'close', 'assignfile',
        'closefile', 'blockwrite', 'blockread', 'seek', 'filepos', 'filesize',
        'truncate', 'flush', 'erase', 'findfirst', 'findnext', 'findclose',
        'getdir', 'setfileattr', 'getfileattr', 'diskfree', 'disksize',
        'chown', 'fpchown', 'link', 'fplink', 'symlink', 'fpsymlink',
        'readlink', 'fpreadlink', 'stat', 'fpstat', 'lstat', 'fplstat',
        'access', 'fpaccess', 'utime', 'fputime', 'loadfromfile', 'savetofile',
        'tfilestream', 'tmemorystream', 'tstringstream', 'savetostream', 'loadfromstream',
        'createdirectory', 'removetree', 'forcedirectories', 'fileexists', 'directoryexists',

        # Memory/pointer manipulation (prevent adding processes in memory)
        'getmem', 'freemem', 'reallocmem', 'ptr', 'addr', 'pointer',
        'allocmem', 'memsize', 'getmemorymanager', 'setmemorymanager',
        'move', 'fillchar', 'fillbyte', 'filldword', 'fillqword',
        'copymemory', 'zeromemory', 'comparemem',

        # Process management (prevent OS process manipulation)
        'fork', 'fpfork', 'shell', 'popen', 'fpexecv', 'fpexecve', 'fpexecvp',
        'waitpid', 'fpwaitpid', 'kill', 'fpkill', 'signal', 'fpsignal',

        # Dynamic loading (prevent loading libraries)
        'loadlibrary', 'getprocaddress', 'freelibrary', 'dlopen', 'dlsym',
        'dlclose', 'dlerror', 'dynlibs',

        # Port access (prevent hardware port manipulation)
        'port', 'portb', 'portw', 'portl', 'inportb', 'outportb', 'inport', 'outport',

        # Shell commands and utilities (prevent command execution)
        'curl', 'wget', 'id', 'echo', 'cat', 'ls', 'rm', 'touch', 'chmod', 'chown',
        'mv', 'cp', 'find', 'grep', 'awk', 'sed', 'tar', 'zip', 'unzip',

        # Units that could compromise security
        'dos', 'dynlibs', 'unix', 'baseunix', 'unixutil', 'windows', 'fileutil',
        'lazfileutils', 'shellapi', 'registry', 'sysutils', 'typinfo', 'variants',
        'printer', 'ports', 'video', 'WinDirs', 'WinCRT', 'ipc', 'go32', 'crt'
    ]
    
    if any(keyword in code.lower() for keyword in dangerous_keywords):
        # Prevent execution of potentially dangerous system calls
        return jsonify({'error': 'Code contains restricted keywords.'}), 400

    # Critical security checks for advanced exploits
    if any(pattern in code.lower() for pattern in [
        # Direct system call exploits
        'syscall', 'cdecl', 'external', 'name', 'nativeuint', 'pchar',
        # Assembly and low-level operations
        'asm', 'inline', '@', 'absolute',
        # External linking and library calls
        'external', 'cdecl', 'stdcall', 'pascal', 'safecall',
        # Pointer operations and memory manipulation
        'pointer', 'ptr', 'addr', '^', '@',
        # System-level constants and types
        'nativeuint', 'nativeint', 'ptruint', 'ptrint',
        # File handles and descriptors
        'thandle', 'handle', 'hfile',
        # Command execution patterns
        '/bin/', '/usr/', '/etc/', 'sh', 'bash', 'cmd',
        # Compiler directives that could be dangerous
        '{$', '(*$', 'include', 'link',
    ]):
        return jsonify({'error': 'Code contains advanced exploit patterns.'}), 400

    # Advanced pattern detection using regex for more sophisticated exploits
    suspicious_patterns = [
        r'external\s+[\'"][^\'\"]*[\'"]',  # External library declarations
        r'syscall\s*\(',                   # Direct system calls
        r'{.*\$.*}',                       # Compiler directives
        r'asm\s+.*end',                    # Assembly blocks
        r'@[a-zA-Z_][a-zA-Z0-9_]*',       # Address operators
        r'\^[a-zA-Z_][a-zA-Z0-9_]*',      # Pointer dereference
        r'/bin/|/usr/|/etc/',              # Unix system paths
        r'sh\s*\-c',                       # Shell command execution
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
            return jsonify({'error': 'Code contains sophisticated exploit patterns.'}), 400

    # Compile and run the Pascal code using our FPC runner module
    output = compile_and_run(code, args, user_input)
    

    # Limit the output size
    if len(output) > MAX_OUTPUT_SIZE:
        output = output[:MAX_OUTPUT_SIZE] + '\n ... (output truncated)'

    # Return the result as JSON (either program output or error messages)
    return jsonify({'output': output})


# Entry point: start the Flask development server
if __name__ == '__main__':
    print(f"Starting Flask server on {HOST}:{backend_port}", flush=True)
    print("Available routes:", flush=True)
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}", flush=True)
    # Run the server with the following configuration:
    # - host='0.0.0.0': Accept connections from any IP address
    # - port=5000: Listen on port 5000
    # - debug=False: Disable debug mode for production-like behavior
    app.run(host=HOST, port=int(backend_port), debug=False)
