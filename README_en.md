# OneTimeEnv

This Docker image provides a convenient way to run a Flask application that allows uploading, extracting, and executing Python scripts along with their dependencies.

## Features

*   Upload `.zip`, `.tar`, `.tar.gz`, or `.tgz` archives containing Python scripts.
*   Automatically extract the uploaded archives.
*   Install dependencies using `pip` and a `requirements.txt` file.
*   Execute Python scripts via a web interface.
*   Real-time output logging through WebSocket connections.

## Prerequisites

*   Docker is installed on your system.

## Usage

### 1. Build the Docker Image

Clone the repository containing the `Dockerfile`, `app.py`, `deploy.sh`, `static/`, and `templates/` files. Then, build the Docker image using the following command:

```bash
docker build -t onetimenv .
```

### 2. Run the Docker Container

Run the Docker container, mapping port 8000 on the host to port 8000 on the container:

```bash
docker run -p 8000:8000 onetimenv
```

### 3. Access the Web Interface

Open your web browser and navigate to `http://localhost:8000`.

### 4. Upload Your Project

1.  Click the "Choose File" button and select your project archive (`.zip`, `.tar`, `.tar.gz`, or `.tgz`).
2.  Click the "Upload" button.
3.  The application will extract the archive to the `/app/uploads/<project name>` directory.

### 5. Run Your Script

1.  Select the Python script you want to run from the dropdown menu.
2.  Enter any command-line arguments in the "Arguments" field.
3.  Click the "Run" button.
4.  The script's output will be displayed in the "Output" section.

## Detailed Explanation of the `Dockerfile`

The `Dockerfile` performs the following actions:

*   Uses `python:3.11-bookworm` as the base image.
*   Installs necessary tools: `nodejs`, `npm`, `zip`, `tar`, `gosu`, and `build-essential`.
*   Creates a non-root user `myuser`.
*   Sets the working directory to `/app`.
*   Copies application files (`app.py`, `deploy.sh`, `static/`, `templates/`).
*   Installs Python dependencies: `flask` and `flask-socketio`.
*   Sets the owner of the `/app/uploads` directory to `myuser`.
*   Switches to the `myuser` user.
*   Exposes port 8000.
*   Executes the `deploy.sh` script.

### Environment Variables

*   **None** - The current image does not use any environment variables. You can add environment variables as needed, such as for configuring database connections or API keys.

## Detailed Explanation of the `deploy.sh` Script

The `deploy.sh` script performs the following actions:

*   Creates the project directory `/app/www/html` and the upload directory `/app/uploads`.
*   Copies static files and templates to the project directory.
*   Starts the Flask application.

## Contributing

Contributions are welcome! Please submit a Pull Request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

*   **Dependency Installation Failure:** If dependency installation fails, check that the `requirements.txt` file is correct and that your container has access to the external network.
*   **Script Execution Errors:** If script execution fails, check the script's syntax and logic, and ensure all necessary dependencies are installed.

## Known Issues

*   **None** - There are currently no known issues.

## Contact

If you have any questions or suggestions, please submit an Issue on GitHub.

## Maintainer

*   zaixia108

## Creation Date

*   2025-02-07

## Version

*   1.0
