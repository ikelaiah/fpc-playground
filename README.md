# 🚀FPC Playground

A simple way to run Free Pascal programs in the browser so new developers can learn the language without having to install anything.

![FPC Playground Screenshot](assets/2025-07-10-1723-screeenshot_00.png)

## Table of Contents
- [🚀FPC Playground](#fpc-playground)
  - [Table of Contents](#table-of-contents)
  - [🌟Features](#features)
  - [✋Prerequisite](#prerequisite)
  - [🏃Running Locally](#running-locally)
    - [Using Docker Compose](#using-docker-compose)
    - [Without Docker Compose](#without-docker-compose)
      - [Backend](#backend)
      - [Frontend](#frontend)
  - [🧪Tests using `curl`](#tests-using-curl)
    - [Test a simple "Hello, World!" program:](#test-a-simple-hello-world-program)
  - [🚩Common Issues](#common-issues)
    - [Double Quotes in Strings](#double-quotes-in-strings)
  - [🙌Contributing](#contributing)
  - [⚖️ License](#️-license)
  - [🙏 Acknowledgments](#-acknowledgments)

## 🌟Features

- **Web-based Pascal editor** with syntax highlighting
- **Real-time compilation** and execution
- **Example programs** to get started quickly
- **Error detection** for common Pascal syntax mistakes
- **Security filtering** to prevent dangerous operations

## ✋Prerequisite

Make sure you have Docker installed. You can download it from [Docker's official site](https://www.docker.com/get-started).


## 🏃Running Locally

### Using Docker Compose

To simplify setup, you can use Docker Compose to run both the backend and frontend services:

1. Clone the repo

```bash
git clone https://github.com/ikelaiah/fpc-playground.git
```

2. Navigate to the project directory

```bash
cd fpc-playground
```

3. Run Docker Compose

```bash
docker-compose up
```

4. Access the frontend at `http://localhost:8080` and the backend at `http://localhost:5000`.

### Without Docker Compose

#### Backend

To run the backend manually without Docker Compose, follow these steps:

1. Clone the repo

```bash
git clone https://github.com/ikelaiah/fpc-playground.git
```

2. Navigate to the `backend` directory

```bash
cd fpc-playground/backend
```

3. Build the Docker image


```bash
docker build -t fpc-playground-backend .
```

4. Run the Docker container

```bash
docker run -p 5000:5000 fpc-playground-backend
```

#### Frontend

The frontend is a simple HTML page that interacts with the backend API using Javascript.

To run the frontend manually, you can simply open the `index.html` file in your web browser. It will automatically connect to the backend running on `http://localhost:5000`.

## 🧪Tests using `curl`

Run the following commands to test the backend using `curl`:

```bash
cd backend
docker build -t fpc-playground-backend .
docker run -p 5000:5000 fpc-playground-backend
``` 

We used the following snippets to test the backend using curl:

### Test a simple "Hello, World!" program:

```bash
cat > test.json << 'EOF'
{"code": "program HelloWorld; begin writeln('Hello, World!'); end."}
EOF
curl -X POST http://localhost:5000/run -H "Content-Type: application/json" -d @test.json
```

## 🚩Common Issues

### Double Quotes in Strings
Pascal uses single quotes `'` for strings, not double quotes `"`. If you use double quotes, you'll get a syntax error.

❌ **Incorrect:**
```pascal
writeln("Hello, World!");
```

✅ **Correct:**
```pascal
writeln('Hello, World!');
```

💡 **Tip:** Use the "🔧 Fix Quotes" button to automatically convert double quotes to single quotes!

## 🙌Contributing
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
    - [Unofficial Free Pascal discord server](https://discord.com/channels/570025060312547359/570091337173696513)
    - [Free Pascal & Lazarus forum](https://forum.lazarus.freepascal.org/index.php)
    - [Tweaking4All Delphi, Lazarus, Free Pascal forum](https://www.tweaking4all.com/forum/delphi-lazarus-free-pascal/)
    - [Laz Planet - Blogspot](https://lazplanet.blogspot.com/) / [Laz Planet - GitLab](https://lazplanet.gitlab.io/)
    - [Delphi Basics](https://www.delphibasics.co.uk/index.html)
- All contributors who have helped improve this project