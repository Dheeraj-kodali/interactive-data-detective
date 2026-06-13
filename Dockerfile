# Use a lightweight official Python base image
FROM python:3.10-slim

# Set environment variables:
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# - PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr, allowing immediate logging
# - HOME: Sets the home directory path for the non-root user
# - PATH: Appends the user's local bin path to search for executables (e.g. streamlit)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Create a non-root user with UID 1000 to comply with Hugging Face Spaces security policies
RUN useradd -m -u 1000 user

# Set the working directory in the container
WORKDIR /code

# Install basic compiler tools required by potential packages (e.g. umap-learn/numba compilation checks)
# and clean up apt cache in the same layer to minimize Docker image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to take advantage of Docker's layer caching
COPY --chown=user:user requirements.txt /code/requirements.txt

# Switch context to the non-root user
USER user

# Install Python dependencies locally in the user home space without cache
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy the rest of the application files, ensuring correct user and group ownership
COPY --chown=user:user . /code

# Expose port 7860 (Hugging Face Spaces default container port)
EXPOSE 7860

# Launch the Streamlit application using the environment configuration
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
