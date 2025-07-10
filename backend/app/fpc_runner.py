import subprocess
import tempfile
import os


def compile_and_run(source_code: str):
    """
    Compiles and runs Free Pascal code in a secure temporary environment.
    
    Args:
        source_code (str): The Pascal source code to compile and execute
        
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
        compile_proc = subprocess.run(
            ['fpc', file_path],                  # Simple: fpc input_file.pas
            stdout=subprocess.PIPE,              # Capture standard output
            stderr=subprocess.STDOUT,            # Redirect stderr to stdout
            cwd=tempdir                          # Set working directory for compilation
        )

        # The executable will be created as 'temp_program' (without .pas extension)
        exe_path = os.path.join(tempdir, 'temp_program')

        # Step 3: Check if compilation was successful
        # If compilation failed, return the error messages from the compiler
        if compile_proc.returncode != 0:
            return compile_proc.stdout.decode('utf-8')
        
        # Step 4: If compilation succeeded, run the compiled executable
        run_proc = subprocess.run(
            [exe_path],                          # Run the compiled program
            stdout=subprocess.PIPE,              # Capture program output
            stderr=subprocess.STDOUT,            # Capture any runtime errors
            timeout=10                           # Prevent infinite loops (10 second limit)
        )

        # Step 5: Return the program's output
        return run_proc.stdout.decode('utf-8')
