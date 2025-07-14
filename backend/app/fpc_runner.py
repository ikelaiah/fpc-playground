import subprocess
import tempfile
import os

# Constants for resource limits
CPU_TIME_LIMIT = 10          # seconds
RAM_LIMIT = 64 * 1024 * 1024 # MB
TIMEOUT_LIMIT = 20           # seconds

def _limit_resources():
    """
    Limit resources for the subprocess (linux only).
    """

    import resource

    # Set the max CPU time in seconds
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_TIME_LIMIT, CPU_TIME_LIMIT))

    # Set max memory usage
    resource.setrlimit(resource.RLIMIT_AS, (RAM_LIMIT, RAM_LIMIT))

    # Additional security limits
    try:
        # Limit number of processes/threads
        resource.setrlimit(resource.RLIMIT_NPROC, (1, 1))
        
        # Limit file size
        resource.setrlimit(resource.RLIMIT_FSIZE, (1024*1024, 1024*1024))  # 1MB max file size
        
        # Limit number of open files
        resource.setrlimit(resource.RLIMIT_NOFILE, (10, 10))
        
        # Disable core dumps
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except:
        pass  # Some limits might not be available on all systems


def compile_and_run(source_code: str, program_args:str = '', user_input: str = '') -> str:
    """
    Compiles and runs Free Pascal code in a secure temporary environment.
    
    Args:
        source_code (str): The Pascal source code to compile and execute
        program_args (str): Arguments to pass to the program
        user_input (str): Input to provide to the program during execution 
        
    Returns:
        str: Either the program output (if successful) or compilation errors
    """
    
    # Create a temporary directory that will be automatically cleaned up
    # This ensures no leftover files and provides isolation between runs
    with tempfile.TemporaryDirectory() as tempdir:
        
        # Step 1: Write the source code to a temporary .pas file
        file_path = os.path.join(tempdir, 'temp_program.pas')
        with open(file_path, 'w') as source_file:
            source_file.write(source_code) 

        # Step 2: Compile the Pascal source code using Free Pascal Compiler (fpc)
        # Note: FPC creates executable with same name as source file (without .pas extension)
        # Add security flags to prevent dangerous operations
        compile_proc = subprocess.run(
            ['fpc', '-Xs-', '-CX', '-XX', '-Sa', '-Sc', '-Se', file_path],  
            # -Xs- strip symbols, -CX no external libs, -XX no external commands
            # -Sa assertions, -Sc support C-style operators, -Se stop after first error
            stdout=subprocess.PIPE,              # Capture standard output
            stderr=subprocess.STDOUT,            # Redirect stderr to stdout
            cwd=tempdir,                         # Set working directory for compilation
            timeout=30,                          # Limit compilation time
            env={'PATH': '/usr/bin:/bin', 'HOME': tempdir, 'TMPDIR': tempdir}  # Restricted environment
        )

        # The executable will be created as 'temp_program' (without .pas extension)
        exe_path = os.path.join(tempdir, 'temp_program')

        # Step 3: Check if compilation was successful
        # If compilation failed, return the error messages from the compiler
        if compile_proc.returncode != 0:
            return compile_proc.stdout.decode('utf-8')
        
        try:
            # Step 4: If compilation succeeded, run the compiled executable
            # Pass the program arguments if provided
            cmd = [exe_path]
            if program_args.strip():
                # Split the program arguments by spaces
                cmd.extend(program_args.split())

            # Step 5: Prepare input for the program
            stdin_input = None
            if user_input.strip():
                stdin_input = user_input
            
            # Step 6: Run the compiled executable with strict security
            run_proc = subprocess.run(
                cmd,
                input=stdin_input,                   # Provide input to the program
                stdout=subprocess.PIPE,              # Capture program output
                stderr=subprocess.STDOUT,            # Capture any runtime errors
                text=True,                           # Decode output as text                
                timeout=TIMEOUT_LIMIT,               # Prevent infinite loops (TIMEOUT_LIMIT)
                preexec_fn=_limit_resources if os.name != 'win32' else None,
                cwd=tempdir,                         # Ensure working directory is isolated
                env={                                # Completely isolated environment
                    'PATH': '',                      # No PATH to prevent command execution
                    'HOME': tempdir,                 # Isolated home directory
                    'TMPDIR': tempdir,               # Isolated temp directory
                    'USER': 'sandbox',               # Non-privileged user
                    'SHELL': '/bin/false'            # Disable shell access
                }
            )
            # Step 7: Return the program's output
            return run_proc.stdout
        except subprocess.TimeoutExpired:
            return "Error: Program execution timed out"
        except Exception as e:
            return f"Error: {str(e)}"