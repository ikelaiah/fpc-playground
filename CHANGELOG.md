# CHANGELOG


## [0.2.1] - 2025-07-14

### Critical Security Fixes

- **System Call Exploit Prevention**: Fixed critical vulnerability where attackers could execute arbitrary system commands using direct syscall invocations with external library declarations.

### Better Security Architecture

- **Multi-layered Input Validation**:
  - Regex-based pattern detection for sophisticated exploits
  - Pre-compilation code validation to reject dangerous patterns
  - Character encoding and code complexity validation
  - Expanded keyword filtering for dangerous operations

- **Compilation & Runtime Hardening**:
  - Strict FPC compiler flags (`-Xs-`, `-CX`, `-XX`, `-Sa`, `-Sc`, `-Se`)
  - Enhanced resource limits (CPU, memory, processes, file descriptors)
  - Completely isolated execution environment with minimal PATH
  - Disabled shell access and prevented core dumps

- **Container Security**:
  - Removed network tools (`curl`, `wget`, `netcat`, `telnet`, `ssh`)
  - Removed system utilities (`cat`, `vim`, `nano`, `git`)
  - Replaced `/bin/sh` with `/bin/false`
  - Running as non-root user (`fpcuser`)

- **Web Security**: Added CSP, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection headers

### Detection Improvements

- **Blocked patterns**: `syscall`, `cdecl`, `external`, `nativeuint`, `pchar`, assembly blocks, Unix paths, shell commands, compiler directives


## [0.2.0] - 2025-07-14

### Added

- **Program Arguments Support**:
  - Added dedicated textarea for entering command line arguments.
  - Arguments are properly parsed and passed to the compiled Pascal program.
  - Supports multiple arguments separated by spaces.

- **User Input Support for ReadLn()**:
  - Added dedicated textarea for providing input to Pascal programs.
  - Supports multiple input lines for sequential `ReadLn()` calls.
  - Input is fed directly to the program's stdin during execution.
  - Educational-friendly approach with clear separation of input/output.

- **Enhanced UI Layout**:
  - Improved responsive design with better panel organization.
  - Added clear labels and helpful placeholder text for input fields.
  - Better visual hierarchy for educational use.


## [0.1.0] - 2025-07-12

### Initial Release

- **Base64 encoding for code transmission**:
  - No JSON escaping issues - base64 contains only safe characters.
  - Proper Unicode handling - `encodeURIComponent` handles all characters correctly.
  - Security - Dangerous keywords can still be checked after decoding.
  - Cleaner transmission - No worries about quotes, newlines, or special characters.
  - Future-proof - No deprecated functions.

- **Web-based Pascal editor**:
  - Syntax highlighting for Pascal code.
  - Real-time compilation and execution.
  - Example programs to help users get started quickly.

- **Frontend features**:
  - "Fix Quotes" button to automatically convert double quotes to single quotes for Pascal compatibility.
  - Resizable code editor and output panel.

- **Backend features**:
  - Security filtering to prevent dangerous operations in Pascal code.
  - Rate limiting to prevent abuse of the API.
  - Error handling for common issues like invalid JSON and syntax errors.