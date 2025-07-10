"""
FPC Playground Backend Server

This Flask application provides a REST API for compiling and running Free Pascal code.
It receives Pascal source code via HTTP POST requests and returns the execution results.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from fpc_runner import compile_and_run
import os

# Server configuration
HOST = '0.0.0.0'  # Listen on all network interfaces (allows external connections)

# Get backend port from environment variable or default to 5000
backend_port = os.getenv('BACKEND_PORT', '5000')

# Initialize Flask application
app = Flask(__name__)

# Enable CORS for all routes (allows frontend to call backend from different origins)
CORS(app)


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

    # Extract Pascal source code from the JSON request body
    # Default to empty string if 'code' field is missing
    code = request.json.get('code', '')

    if len(code) > 10000:
        # Limit the size of the code to prevent usage abuse
        return jsonify({'error' : 'Code size exceeds limit of 10,000 characters.'}), 400

    # List of dangerous Pascal procedures/functions that could compromise security
    dangerous_keywords = [
        # System command execution
        'system', 'fpsystem', 'exec', 'execl', 'execv', 'execve', 'execvp',
        
        # Process management
        'fork', 'fpfork', 'shell', 'popen', 'fpexecv', 'fpexecve', 'fpexecvp',
        
        # File system operations (potentially dangerous)
        'deletefile', 'removedir', 'rename', 'rmdir', 'unlink', 'fpunlink',
        'mkdir', 'fpmkdir', 'chdir', 'fpchdir', 'chmod', 'fpchmod',
        
        # Network operations
        'socket', 'bind', 'listen', 'accept', 'connect', 'fpsocket',
        
        # Memory/pointer manipulation (advanced, potentially unsafe)
        'getmem', 'freemem', 'reallocmem', 'ptr', 'addr',
        
        # Dynamic loading
        'loadlibrary', 'getprocaddress', 'freelibrary',
        
        # Environment manipulation
        'setenv', 'fpsetenv', 'getenv', 'fpgetenv', 'putenv', 'fpputenv',
        
        # Other potentially dangerous operations
        'asm'
    ]
    
    if any(keyword in code.lower() for keyword in dangerous_keywords):
        # Prevent execution of potentially dangerous system calls
        return jsonify({'error': 'Code contains restricted keywords that could compromise security.'}), 400

    # Compile and run the Pascal code using our FPC runner module
    output = compile_and_run(code)
    
    # Return the result as JSON (either program output or error messages)
    return jsonify({'output': output})


# Entry point: start the Flask development server
if __name__ == '__main__':
    # Run the server with the following configuration:
    # - host='0.0.0.0': Accept connections from any IP address
    # - port=5000: Listen on port 5000
    # - debug=False: Disable debug mode for production-like behavior
    app.run(host=HOST, port=int(backend_port), debug=False)