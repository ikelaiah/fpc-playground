// Simple FPC Playground JavaScript

// Example Pascal programs
const examples = [
    // Hello World
`program HelloWorld;

{$mode objfpc}{$H+}{$J-}

begin
  writeln('Hello, Free Pascal!');
  writeln('Welcome to the FPC Playground!');
end.`,
    
    // Variables
`program Variables;

{$mode objfpc}{$H+}{$J-}

var
  name: string;
  age: integer;
  pi: real;
begin
  name := 'Pascal Programmer';
  age := 25;
  pi := 3.14159;
  
  writeln('Name: ', name);
  writeln('Age: ', age);
  writeln('Pi: ', pi:0:5);
end.`,
    
    // Loops
`program Loops;

{$mode objfpc}{$H+}{$J-}

var
  i: integer;

begin
  writeln('Counting with for loop:');
  for i := 1 to 5 do
    writeln('Count: ', i);
    
  writeln('Countdown with while loop:');
  i := 5;
  while i > 0 do
  begin
    writeln('Countdown: ', i);
    i := i - 1;
  end;
  writeln('Blast off!');
end.`,
    
    // String handling
`program StringDemo;

{$mode objfpc}{$H+}{$J-}

var
  message: string;
  count: integer;

begin
  { Note: Pascal uses single quotes for strings }
  message := 'Hello, World!';
  count := Length(message);
  
  writeln('Message: ', message);
  writeln('Length: ', count);
  writeln('Uppercase: ', UpCase(message));
end.`
];

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Wait for Ace editor to be available
    const waitForEditor = setInterval(() => {
        if (window.aceEditor) {
            clearInterval(waitForEditor);
            initializePlayground();
        }
    }, 500);
});

function initializePlayground() {
    const editor = window.aceEditor;
    const runBtn = document.getElementById('run-btn');
    const clearBtn = document.getElementById('clear-btn');
    const fixQuotesBtn = document.getElementById('fix-quotes-btn');
    const output = document.getElementById('output');
    const exampleBtns = document.querySelectorAll('.example-code');

    // Example button clicks
    console.log('Found example buttons:', exampleBtns.length);
    exampleBtns.forEach(btn => {
        console.log('Adding click listener to:', btn.id, 'with data-example:', btn.dataset.example);
        btn.addEventListener('click', () => {
            const exampleIndex = parseInt(btn.dataset.example);
            console.log('Example button clicked:', exampleIndex);
            loadExample(exampleIndex);
        });
    });

    // Run button click
    runBtn.addEventListener('click', runCode);

    // Clear button click
    clearBtn.addEventListener('click', clearCode);

    // Fix quotes button click
    fixQuotesBtn.addEventListener('click', fixQuotes);

    function loadExample(index) {
        console.log('Loading example:', index, 'Total examples:', examples.length);
        if (index >= 0 && index < examples.length) {
            editor.setValue(examples[index], -1); // -1 moves cursor to start
            output.textContent = 'Loaded example: ' + examples[index].split('\n')[0].replace('program', '');
        } else {
            console.error('Invalid example index:', index);
        }
    }

    function clearCode() {
        editor.setValue('', -1);
        output.textContent = 'Ready to run your Pascal code...';
    }

    function fixQuotes() {
        const code = editor.getValue();
        if (code.includes('"')) {
            // Replace double quotes with single quotes in string literals
            const fixedCode = code.replace(/"/g, "'");
            editor.setValue(fixedCode, -1);
            output.textContent = '✅ Fixed: Replaced double quotes with single quotes for Pascal compatibility.';
        } else {
            output.textContent = '✅ No double quotes found. Your code looks good!';
        }
    }

    // Update backend URL dynamically based on environment
    const backendUrl = window.location.hostname.includes('fpc-playground-app-mgeib.ondigitalocean.app/')
      ? 'https://fpc-playground-app-mgeib.ondigitalocean.app'
      : 'http://localhost:5000';

    async function runCode() {
        const code = editor.getValue().trim();
        
        if (!code) {
            output.textContent = 'Please enter some Pascal code to run.';
            return;
        }

        // Check for common Pascal syntax errors
        if (code.includes('"')) {
            // Check if it's used in string literals (common mistake)
            const doubleQuotePattern = /writeln\s*\(\s*"[^"]*"\s*\)/i;
            const printPattern = /write\s*\(\s*"[^"]*"\s*\)/i;
            
            if (doubleQuotePattern.test(code) || printPattern.test(code)) {
                output.textContent = '❌ Pascal Syntax Error: Use single quotes (\') for strings, not double quotes (").\n\n' +
                    'Correct: writeln(\'Hello, World!\');\n' +
                    'Incorrect: writeln("Hello, World!");\n\n' +
                    '💡 Tip: Click the "🔧 Fix Quotes" button to automatically fix this!';
                return;
            }
            
            // General warning for any double quotes
            output.textContent = '❌ Pascal Syntax Error: Pascal uses single quotes (\') for strings, not double quotes (").\n\n' +
                'Please replace all " with \' in your string literals.\n\n' +
                '💡 Tip: Click the "🔧 Fix Quotes" button to automatically fix this!';
            return;
        }

        // Update UI to show loading state
        runBtn.disabled = true;
        runBtn.textContent = '⏳ Running...';
        output.textContent = 'Compiling and running your Pascal code...';

        try {
            // Prepare the request payload
            const payload = { code: code };
            
            // Send code to backend
            const response = await fetch(backendUrl + '/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            // Display output or format compiler errors nicely
            if (result.output) {
                // Check if it's a compiler error
                if (result.output.includes('Fatal:') || result.output.includes('Error:')) {
                    // Format compiler errors for better readability
                    const formattedError = result.output
                        .replace(/temp_program\.pas\(\d+,\d+\)/g, 'Line $&')
                        .replace(/Fatal: /g, '❌ Fatal Error: ')
                        .replace(/Error: /g, '❌ Error: ')
                        .replace(/temp_program\.pas/g, 'Your code');
                    
                    output.textContent = formattedError;
                } else {
                    // Regular program output
                    output.textContent = result.output;
                }
            } else {
                output.textContent = 'No output';
            }

        } catch (error) {
            output.textContent = `❌ Connection Error: ${error.message}\n\n💡 Make sure the backend server is running.`;
        } finally {
            // Reset button state
            runBtn.disabled = false;
            runBtn.textContent = '▶ Run Code';
        }
    }
}