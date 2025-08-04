"""
FPC Playground Backend Server

This Flask application provides a REST API for compiling and running Free Pascal code.
It receives Pascal source code via HTTP POST requests and returns the execution results.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from fpc_runner import compile_and_run
import base64
import os
import re

# Server configuration
HOST = '0.0.0.0'  # Listen on all network interfaces (allows external connections)

MAX_CODE_SIZE = 16 * 1024    # Max number of characters allowed in pascal code
MAX_OUTPUT_SIZE = 48 * 1024  # Max number of characters output
MAX_ARGS_SIZE = 64          # Max number of characters allowed in program arguments
MAX_INPUT_SIZE = 64         # Max number of characters allowed in user input

# Code complexity limits
MAX_BEGIN_COUNT = 20        # Maximum number of 'begin' statements
MAX_PARENTHESES_COUNT = 100 # Maximum number of parentheses
MAX_BRACKETS_COUNT = 50     # Maximum number of brackets

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

# Helper functions for validation and error handling
def create_error_response(message: str, status_code: int = 400):
    """Create a standardized error response."""
    return jsonify({'error': message}), status_code

def validate_input_sizes(code: str, args: str, user_input: str):
    """Validate input size limits. Returns (is_valid, error_response)."""
    if len(code) > MAX_CODE_SIZE:
        return False, create_error_response(f'Code size exceeds limit of {MAX_CODE_SIZE:,} characters.')
    
    if len(args) > MAX_ARGS_SIZE:
        return False, create_error_response(f'Program arguments size exceeds limit of {MAX_ARGS_SIZE:,} characters.')
    
    if len(user_input) > MAX_INPUT_SIZE:
        return False, create_error_response(f'User input size exceeds limit of {MAX_INPUT_SIZE:,} characters.')
    
    return True, None

def validate_code_complexity(code: str):
    """Validate code complexity limits. Returns (is_valid, error_response)."""
    if (code.count('begin') > MAX_BEGIN_COUNT or 
        code.count('(') > MAX_PARENTHESES_COUNT or 
        code.count('[') > MAX_BRACKETS_COUNT):
        return False, create_error_response('Code structure too complex.')
    
    return True, None

def validate_character_encoding(code: str):
    """Validate input characters to prevent encoding attacks. Returns (is_valid, error_response)."""
    if any(ord(char) < 32 or ord(char) > 126 for char in code if char not in '\n\r\t'):
        return False, create_error_response('Code contains invalid characters.')
    
    return True, None

def validate_security_patterns(code: str):
    """Comprehensive security validation for dangerous patterns. Returns (is_valid, error_response)."""
    code_lower = code.lower()
    
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
        'dos', 'dynlibs', 'unix', 'baseunix', 'unixutil', 'windows', 
        'fileutil', 'lazfileutils', 'shellapi', 'registry',
        'printer', 'ports', 'video', 'WinDirs', 'WinCRT', 'ipc', 'go32', 'crt'
    ]
    
    # Critical security checks for advanced exploits
    exploit_patterns = [
        # Direct system call exploits
        'syscall', 'cdecl', 'nativeuint', 'pchar',
        # Assembly and low-level operations
        'asm', 'inline', 'absolute',
        # External linking and library calls
        'stdcall', 'safecall',
        # Pointer operations and memory manipulation
        'pointer', 'ptr', 'addr',
        # System-level constants and types
        'ptruint', 'ptrint',
        # File handles and descriptors
        'thandle', 'hfile',
    ]
    
    # Path patterns that use substring matching
    path_patterns = ['/bin/', '/usr/', '/etc/']
    
    # Shell commands that need word boundary matching
    shell_commands = ['bash', 'cmd']
    
    # Special check for 'sh' - only block if it appears as a standalone command or with specific patterns
    sh_dangerous_patterns = [
        r'\bsh\s+\-c',  # sh -c command
        r'\bsh\s+["\']',  # sh "command" or sh 'command'
        r'/bin/sh',  # path to sh
        r'\bsh\s*\(',  # sh() function call
        r'\bsh\s*;',  # sh; (command separator)
        r'\bsh\s*$',  # sh at end of line
    ]

    # Special patterns that need exact character matching (not word boundaries)
    special_chars = ['@', '^']

    # Check for dangerous keywords using word boundaries to prevent false positives
    for keyword in dangerous_keywords:
        # Use regex with word boundaries to match only complete identifiers
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, code_lower, re.IGNORECASE):
            return False, create_error_response(f'Code contains restricted keyword: {keyword}')

    # Check regular exploit patterns with word boundaries
    for pattern in exploit_patterns:
        regex_pattern = r'\b' + re.escape(pattern) + r'\b'
        if re.search(regex_pattern, code_lower, re.IGNORECASE):
            return False, create_error_response(f'Code contains exploit pattern: {pattern}')
    
    # Check path patterns with substring matching
    for pattern in path_patterns:
        if pattern in code_lower:
            return False, create_error_response(f'Code contains exploit pattern: {pattern}')
    
    # Check shell commands with word boundaries to avoid false positives
    for pattern in shell_commands:
        regex_pattern = r'\b' + re.escape(pattern) + r'\b'
        if re.search(regex_pattern, code_lower, re.IGNORECASE):
            return False, create_error_response(f'Code contains exploit pattern: {pattern}')
    
    for pattern in sh_dangerous_patterns:
        if re.search(pattern, code_lower, re.IGNORECASE):
            return False, create_error_response('Code contains shell execution pattern')
    
    # Check for special characters that could be dangerous
    for char in special_chars:
        if char in code:
            return False, create_error_response(f'Code contains restricted character: {char}')
    
    return True, None

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

    # Check if the request body can be parsed as JSON
    try:
        json_data = request.get_json(force=True)
        encodedCode = json_data.get('code', '')
        encodedArgs = json_data.get('args', '')
        encodedInput = json_data.get('input', '')
    except Exception:
        return jsonify({'error': 'Invalid JSON'}), 400

    code = base64.b64decode(encodedCode).decode('utf-8')
    args = base64.b64decode(encodedArgs).decode('utf-8')
    user_input = base64.b64decode(encodedInput).decode('utf-8')

    # Validate input sizes
    is_valid, error_response = validate_input_sizes(code, args, user_input)
    if not is_valid:
        return error_response

    # Validate character encoding
    is_valid, error_response = validate_character_encoding(code)
    if not is_valid:
        return error_response

    # Validate code complexity
    is_valid, error_response = validate_code_complexity(code)
    if not is_valid:
        return error_response

    # Validate security patterns
    is_valid, error_response = validate_security_patterns(code)
    if not is_valid:
        return error_response


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
