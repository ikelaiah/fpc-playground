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
import os

# Server configuration
HOST = '0.0.0.0'  # Listen on all network interfaces (allows external connections)

MAX_CODE_SIZE = 16 * 1024    # Max number of characters allowed in pascal code
MAX_OUTPUT_SIZE = 48 * 1024  # Max number of characters output


# Get backend port from environment variable or default to 5000
backend_port = os.getenv('BACKEND_PORT', '5000')

# Initialize Flask application
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per hour", "10 per minute"],
    storage_uri="memory://",
)

# Enable CORS for all routes (allows frontend to call backend from different origins)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
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
        code = request.get_json(force=True).get('code', '')
    except Exception:
        return jsonify({'error':'Invalid JSON'}), 400

    # Extract Pascal source code from the JSON request body
    # Default to empty string if 'code' field is missing
    code = request.json.get('code', '')

    # Check if the code exceeds the maximum allowed size
    if len(code) > MAX_CODE_SIZE:
        # Limit the size of the code to prevent usage abuse
        return jsonify({'error' : f'Code size exceeds limit of {MAX_CODE_SIZE:,} characters.'}), 400

    # List of dangerous Pascal procedures/functions that could compromise security
    dangerous_keywords = [
        # System command execution
        'system', 'fpsystem', 'exec', 'execl', 'execv', 'execve', 'execvp',
        'winexec', 'shellexecute', 'createprocess',
        
        # Process management
        'fork', 'fpfork', 'shell', 'popen', 'fpexecv', 'fpexecve', 'fpexecvp',
        'waitpid', 'fpwaitpid', 'kill', 'fpkill', 'signal', 'fpsignal',
        
        # File system operations (potentially dangerous - NO local file saving allowed)
        'deletefile', 'removedir', 'rename', 'rmdir', 'unlink', 'fpunlink',
        'mkdir', 'fpmkdir', 'chdir', 'fpchdir', 'chmod', 'fpchmod',
        'assign', 'rewrite', 'append', 'reset', 'close', 'assignfile',
        'closefile', 'blockwrite', 'blockread', 'seek', 'filepos', 'filesize',
        'truncate', 'flush', 'erase', 'findfirst', 'findnext', 'findclose',
        'getdir', 'setfileattr', 'getfileattr', 'diskfree', 'disksize',
        'chown', 'fpchown', 'link', 'fplink', 'symlink', 'fpsymlink',
        'readlink', 'fpreadlink', 'stat', 'fpstat', 'lstat', 'fplstat',
        'access', 'fpaccess', 'utime', 'fputime', 'loadfromfile'
        
        # Network operations
        'socket', 'bind', 'listen', 'accept', 'connect', 'fpsocket',
        'fpbind', 'fplisten', 'fpaccept', 'fpconnect', 'send', 'recv',
        'fpsend', 'fprecv', 'sendto', 'recvfrom', 'fpsendto', 'fprecvfrom',
        'setsockopt', 'getsockopt', 'fpsetsockopt', 'fpgetsockopt',
        'shutdown', 'fpshutdown', 'gethostbyname', 'gethostbyaddr',
        'getservbyname', 'getservbyport', 'inet_addr', 'inet_ntoa',
        
        # Memory/pointer manipulation (advanced, potentially unsafe)
        'getmem', 'freemem', 'reallocmem', 'ptr', 'addr', 'pointer',
        'allocmem', 'memsize', 'getmemorymanager', 'setmemorymanager',
        'move', 'fillchar', 'fillbyte', 'filldword', 'fillqword',
        'copymemory', 'zeromemory', 'comparemem',
        
        # Dynamic loading
        'loadlibrary', 'getprocaddress', 'freelibrary', 'dlopen', 'dlsym',
        'dlclose', 'dlerror', 'dynlibs',
        
        # Environment manipulation
        'setenv', 'fpsetenv', 'getenv', 'fpgetenv', 'putenv', 'fpputenv',
        'unsetenv', 'fpunsetenv', 'clearenv', 'fpclearenv',
        'getenvironmentvariable', 'setenvironmentvariable',
        
        # Registry operations (Windows)
        'registry', 'regcreatekey', 'regsetvalue', 'regdeletekey',
        'regdeletevalue', 'regqueryvalue', 'regopenkey', 'regclosekey',
        
        # Threading and synchronization (can be used for DoS)
        'beginthread', 'endthread', 'createthread', 'terminatethread',
        'suspendthread', 'resumethread', 'waitforsingleobject',
        'waitformultipleobjects', 'createmutex', 'createevent',
        'createsemaphore', 'criticalsection',
        
        # Time-based attacks and delays
        'sleep', 'delay', 'fpsleep', 'nanosleep', 'fpnanosleep',
        
        # Interrupt handling
        'setintvec', 'getintvec', 'intr',
        
        # Direct hardware access
        'port', 'portb', 'portw', 'portl', 'memw', 'meml', 'mem',
        'inportb', 'outportb', 'inport', 'outport',
        
        # Assembly and low-level operations
        'asm', 'absolute',
        
        # Unit/module inclusion that could be dangerous
        'dos', 'linux', 'windows', 'unix', 'baseunix', 'unixutil',
        'winsock', 'sockets', 'netdb', 'process', 'dynlibs'

        # More file operations
        'copyfile', 'movefile', 'createdir', 'forcedirectories', 'removetree',
        'extractfilepath', 'extractfilename', 'extractfiledir', 'extractfileext',
        'changefileext', 'expandfilename', 'fileexists', 'directoryexists',
        'fileage', 'filedatetimetofiletime', 'filetimetofiledatetime',
        'filegetdate', 'filesetdate', 'filegetattr', 'filesetattr',
        'selectdirectory', 'createdirectory', 'gettempdirectory', 'gettempfilename',
        
        # Stream operations (can access files)
        'filestream', 'createfilestream', 'openfilestream', 'tfilestream',
        'tmemorystream', 'tstringstream', 'savetostream', 'loadfromstream',
        'savetofile', 'createstream',
        
        # More Windows-specific dangerous operations
        'copyfileex', 'movefileex', 'createfile', 'createfilemapping',
        'mapviewoffile', 'unmapviewoffile', 'setfilepointer', 'setendoffile',
        'getfilesize', 'getfiletime', 'setfiletime', 'getfileattributes',
        'setfileattributes', 'findfirstfile', 'findnextfile', 'getlogicaldrives',
        'getdrivetype', 'getdiskfreespace', 'setcurrentdirectory',
        'getcurrentdirectory', 'createpipe', 'duplicatehandle',
        
        # Database operations (potential data access)
        'sqlopen', 'sqlexec', 'sqlquery', 'database', 'opendatabase',
        'closedatabase', 'execsql', 'openquery', 'closequery',
        
        # Compression/archive operations
        'compress', 'decompress', 'zip', 'unzip', 'gzip', 'gunzip',
        'extract', 'archive', 'addfile', 'extractfile',
        
        # Configuration and settings access
        'inifiles', 'readini', 'writeini', 'tinifile', 'readstring',
        'writestring', 'readsection', 'writesection', 'erasesection',
        
        # RTTI and reflection (can access internals)
        'published', 'rtti', 'typeinfo', 'getpropinfo', 'setpropvalue',
        'getpropvalue', 'ispublishedprop', 'typinfo',
        
        # More Unix/Linux system calls
        'fpopen', 'fpclose', 'fpread', 'fpwrite', 'fplseek', 'fpdup',
        'fpdup2', 'fppipe', 'fpselect', 'fpmmap', 'fpmunmap',
        'fpgetpid', 'fpgetppid', 'fpgetuid', 'fpgetgid', 'fpsetuid',
        'fpsetgid', 'fpseteuid', 'fpsetegid', 'fpumask', 'fpgetcwd',
        
        # Variant and OLE operations (Windows)
        'variant', 'olevariant', 'vartype', 'varclear', 'varcast',
        'varastype', 'createoleobject', 'getactiveoleobject',
        
        # More networking
        'gethostname', 'getdomainname', 'sethostname', 'setdomainname',
        'getprotobyname', 'getprotobynumber', 'htons', 'htonl', 'ntohs', 'ntohl',
        
        # More Windows services
        'startservice', 'stopservice', 'controlservice', 'queryservice',
        'installservice', 'deleteservice', 'openservice', 'closeservice',
        
        # Timing attacks and benchmarking
        'gettickcount', 'timegettime', 'queryperformancecounter',
        'queryperformancefrequency', 'rdtsc',
        
        # Additional units that should be blocked
        'registry', 'shellapi', 'comobj', 'inifiles',
        'fileutil', 'lazfileutils', 'lclintf', 'forms', 'dialogs',
        'masks', 'rtti'
    ]
    
    if any(keyword in code.lower() for keyword in dangerous_keywords):
        # Prevent execution of potentially dangerous system calls
        return jsonify({'error': 'Code contains restricted keywords.'}), 400

    # Compile and run the Pascal code using our FPC runner module
    output = compile_and_run(code)
    

    # Limit the output size
    if len(output) > MAX_OUTPUT_SIZE:
        output = output[:MAX_OUTPUT_SIZE] + '\n ... (output truncated)'

    # Return the result as JSON (either program output or error messages)
    return jsonify({'output': output})


# Entry point: start the Flask development server
if __name__ == '__main__':
    # Run the server with the following configuration:
    # - host='0.0.0.0': Accept connections from any IP address
    # - port=5000: Listen on port 5000
    # - debug=False: Disable debug mode for production-like behavior
    app.run(host=HOST, port=int(backend_port), debug=False)
