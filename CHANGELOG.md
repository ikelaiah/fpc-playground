# CHANGELOG

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