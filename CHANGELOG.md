# CHANGELOG


## [0.2.1] - 2025-07-14

### Critical Security Fixes

- **System Call Exploit Prevention**: Fixed critical vulnerability where attackers could execute arbitrary system commands using direct syscall invocations with external library declarations.
- **Advanced Pattern Detection**: Added comprehensive regex-based detection for sophisticated exploits including:
  - External library declarations (`external 'c' name 'syscall'`)
  - Direct system calls and low-level operations
  - Assembly code blocks and inline assembly
  - Pointer operations and memory manipulation
  - Unix system paths and shell command patterns
  - Compiler directives that could bypass security

### Enhanced Security Measures

- **Multi-layered Input Validation**:
  - Pre-compilation code validation to reject dangerous patterns
  - Character encoding validation to prevent encoding attacks
  - Code complexity limits to prevent resource exhaustion
  - Enhanced keyword filtering with expanded dangerous operations list

- **Compilation Security**:
  - Added strict FPC compiler flags (`-Xs-`, `-CX`, `-XX`, `-Sa`, `-Sc`, `-Se`)
  - Restricted compilation environment with limited PATH
  - Compilation timeout to prevent hanging builds
  - Isolated temporary directories for each compilation

- **Runtime Protection**:
  - Enhanced resource limits (CPU, memory, processes, file descriptors)
  - Completely isolated execution environment
  - Disabled shell access (`SHELL=/bin/false`)
  - Prevented core dumps and external command execution
  - Strict environment variable control

- **Web Security Headers**:
  - Added Content Security Policy (CSP)
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection headers

- **Docker Container Hardening**:
  - Explicitly removed network tools (`curl`, `wget`, `netcat`, `telnet`, `ssh`)
  - Removed system utilities (`cat`, `more`, `less`, `vim`, `nano`, `git`)
  - Disabled shell access by replacing `/bin/sh` with `/bin/false`
  - Running as non-root user (`fpcuser`) for enhanced security
  - Minimal attack surface with only essential binaries remaining

### Security Keywords Expanded

- **Added detection for**: `syscall`, `cdecl`, `external`, `nativeuint`, `pchar`, pointer operations, assembly blocks, Unix paths, shell commands, and compiler directives
- **Enhanced filtering**: Now blocks sophisticated attacks using external library calls and direct system calls


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