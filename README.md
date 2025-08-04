# 🚀 FPC Playground

[![License: MIT](https://img.shields.io/badge/License-MIT-1E3A8A.svg)](https://opensource.org/licenses/MIT)
[![Free Pascal](https://img.shields.io/badge/Free%20Pascal-3.2.2+-3B82F6.svg)](https://www.freepascal.org/)
![Python](https://img.shields.io/badge/Python-3.9+-A7F3D0?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-A7F3D0?logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-20.10+-2496ED?logo=docker)
![Web](https://img.shields.io/badge/Web-HTML%2FCSS%2FJS-E34F26?logo=html5)
![Supports Windows](https://img.shields.io/badge/support-Windows-F59E0B?logo=Windows)
![Supports Linux](https://img.shields.io/badge/support-Linux-F59E0B?logo=Linux)
[![Version](https://img.shields.io/badge/version-0.3.0-8B5CF6.svg)](CHANGELOG.md)


A simple way to run Free Pascal programs in the browser so new developers can learn the language without having to install anything.

Give it a try here: [FPC Playground](https://fpc-playground-app-mgeib.ondigitalocean.app/)

> [!WARNING]
> Not production ready yet. This project is still a work in progress and will not support all Free Pascal features.

![FPC Playground Screenshot](assets/2025-07-14-0832-screenshot_00.png)

## Table of Contents
- [🚀 FPC Playground](#-fpc-playground)
  - [Table of Contents](#table-of-contents)
  - [🌟 Features](#-features)
  - [✋ Prerequisites](#-prerequisites)
  - [🚀 Quick Start](#-quick-start)
  - [⭐ Feedback](#-feedback)
  - [🏃 Running Locally](#-running-locally)
    - [Using Docker Compose](#using-docker-compose)
  - [🎓 Using the Playground](#-using-the-playground)
    - [**Code Editor**](#code-editor)
    - [**Program Arguments**](#program-arguments)
    - [**User Input**](#user-input)
    - [**Example Usage**](#example-usage)
    - [Without Docker Compose](#without-docker-compose)
      - [Backend](#backend)
      - [Frontend](#frontend)
  - [🧪 Testing with `curl`](#-testing-with-curl)
    - [Test a simple "Hello, World!" program](#test-a-simple-hello-world-program)
  - [🙌 Contributing](#-contributing)
  - [⚖️ License](#️-license)
  - [🙏 Acknowledgments](#-acknowledgments)

## 🌟 Features

- **Web-based Pascal editor** with syntax highlighting
- **Real-time compilation** and execution
- **Program arguments support** - Pass command line arguments to your Pascal programs
- **User input support** - Handle `ReadLn()` statements with dedicated input fields
- **Example programs** to get started quickly
- **Error detection** for common Pascal syntax mistakes
- **Security filtering** to prevent dangerous operations
- **Educational-friendly interface** with clear separation of code, input, and output

## ✋ Prerequisites

Make sure you have Docker installed. You can download it from [Docker's official site](https://www.docker.com/get-started).

## 🚀 Quick Start
1. Clone the repository: `git clone https://github.com/ikelaiah/fpc-playground.git`
2. Run Docker Compose: `docker-compose up`
3. Access the frontend at `http://localhost:8080` and start coding!

## ⭐ Feedback
We value your feedback! If you enjoy using FPC Playground, please star the repository and share your thoughts.

## 🏃 Running Locally

### Using Docker Compose

To simplify setup, you can use Docker Compose to run both the backend and frontend services:

1. Clone the repository:

```bash
git clone https://github.com/ikelaiah/fpc-playground.git
```

2. Navigate to the project directory:

```bash
cd fpc-playground
```

3. Run Docker Compose:

```bash
docker-compose up
```

4. Access the frontend at `http://localhost:8080` and the backend at `http://localhost:5000`.

## 🎓 Using the Playground

The FPC Playground provides an intuitive interface for learning Pascal programming:

### **Code Editor**
- Write your Pascal code with syntax highlighting
- Use the example buttons to load pre-written programs
- Fix quotes automatically for Pascal compatibility

### **Program Arguments**
- Use the "Program Arguments" textarea to pass command line arguments to your program
- Separate multiple arguments with spaces
- Example: `arg1 arg2 arg3`

### **User Input**
- Use the "User Input" textarea to provide input for `ReadLn()` statements
- Enter each input value on a separate line
- The program will read these values in order when it encounters `ReadLn()`

### **Example Usage**
```pascal
program TestInput;
var
    name: string;
    age: integer;
begin
    writeln('What is your name?');
    readln(name);
    writeln('How old are you?');
    readln(age);
    writeln('Hello ', name, ', you are ', age, ' years old!');
end.
```

For this program, enter in the User Input field:
```
John
25
```

The output will be:
```
What is your name?
How old are you?
Hello John, you are 25 years old!
```

### Without Docker Compose

#### Backend

To run the backend manually without Docker Compose, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/ikelaiah/fpc-playground.git
```

2. Navigate to the `backend` directory:

```bash
cd fpc-playground/backend
```

3. Build the Docker image:

```bash
docker build -t fpc-playground-backend .
```

4. Run the Docker container:

```bash
docker run -p 5000:5000 fpc-playground-backend
```

#### Frontend

The frontend is a simple HTML page that interacts with the backend API using JavaScript.

To run the frontend manually, you can simply open the `index.html` file in your web browser. It will automatically connect to the backend running on `http://localhost:5000`.

## 🧪 Testing with `curl`

Run the following commands to test the backend using `curl`:

```bash
cd backend
docker build -t fpc-playground-backend .
docker run -p 5000:5000 fpc-playground-backend
```

### Test a simple "Hello, World!" program

```bash
cat > test.json << 'EOF'
{"code": "program HelloWorld; begin writeln('Hello, World!'); end."}
EOF
curl -X POST http://localhost:5000/run -H "Content-Type: application/json" -d @test.json
```

## 🙌 Contributing
We welcome contributions! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m "Add feature"`).
4. Push to your branch (`git push origin feature-branch`).
5. Open a pull request.

## ⚖️ License

MIT License - see [LICENSE](LICENSE.md) file for details.

## 🙏 Acknowledgments

- [Free Pascal Dev Team](https://www.freepascal.org/) for the Pascal compiler
- [Lazarus IDE Team](https://www.lazarus-ide.org/) for such an amazing IDE
- The kind and helpful individuals on various online platforms such as:
    - [Unofficial Free Pascal Discord server](https://discord.com/channels/570025060312547359/570091337173696513)
    - [Free Pascal & Lazarus forum](https://forum.lazarus.freepascal.org/index.php)
    - [Tweaking4All Delphi, Lazarus, Free Pascal forum](https://www.tweaking4all.com/forum/delphi-lazarus-free-pascal/)
    - [Laz Planet - Blogspot](https://lazplanet.blogspot.com/) / [Laz Planet - GitLab](https://lazplanet.gitlab.io/)
    - [Delphi Basics](https://www.delphibasics.co.uk/index.html)
- All contributors who have helped improve this project