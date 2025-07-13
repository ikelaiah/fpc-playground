# CHANGELOG

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

### Fixed

- **Backend Parameter Passing**: Fixed critical bug where program arguments and user input were not being passed to the compilation function.
- **Text Encoding**: Improved text handling in subprocess calls with proper `text=True` parameter.

### Technical Improvements

- **Simplified Input Handling**: Direct stdin feeding instead of temporary file approach for better performance.
- **Better Error Handling**: Enhanced error messages for compilation and runtime issues.
- **Code Organization**: Cleaner separation of concerns between frontend and backend components.


## [0.1.0] - 2025-07-12

### Added

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
  - Error handling for common issues like invalid JSON

## [0.1.0] - 2025-07-12

### Added

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