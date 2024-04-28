# Overview

The backend runs on Flask, a web microframework, running on Python. API routes are defined under `server.py` and acts as a middleman to make calls to ChatGPT (or Claude) and return the payload to the frontend. In production, the application runs from a Docker container, but you can run the Flask server directly if you wish without Docker for development (read [Quickstart](#Quickstart)).

# Quickstart

First, set up your Python virtual environment, activate it, and install necessary packages.

```bash
python -m venv venv # setup venv
source venv/bin/activate # activate your virtual environment
pip install -r requirements.txt # install necessary packages
```

You can spin up the backend server without Docker if you wish:

```bash
python server.py
```

Please note that this method may not mirror the production environment closely, and it's recommended to use Docker for a more accurate testing environment.

# Contributing

When adding new Python packages, please remember to update the requirements.txt file. This file is used by Docker to install necessary dependencies. To update the requirements.txt file, please run:

```bash
pip freeze > requirements.txt
```

This command should be run from within the virtual environment to capture the correct list of packages.

# Docker

If you'd like to run Docker, you need to have Docker installed on your machine. If you don't have Docker installed, you can download it from here: https://www.docker.com/products/docker-desktop.

## Building the Docker Image

In order to run a Docker container, you must first build the Docker image for the application, navigate to the project root directory and run:

```bash
docker build -t robo-form-app .
```

This command will pull the Python base image, install all necessary packages from the `requirements.txt` file, and set up the application which runs on a WSGI server setup by Gunicorn.

## Running the Docker Container

Once the Docker image has been built, you can start the container by running:

```bash
docker run -p 4000:80 robo-form-app
```

This command will start the Docker container and bind port 80 inside the container (where our application is running) to port 4000 on your machine. You can then access the application at http://localhost:4000.
