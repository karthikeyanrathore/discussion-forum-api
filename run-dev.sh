#!/usr/bin/env bash
set -e

echo "Starting backend (Docker)..."
docker-compose up -d

echo "Waiting for backend to be ready..."
sleep 5

echo "Starting frontend (static server)..."
cd frontend

# Use Python's built-in HTTP server for simplicity
python3 -m http.server 3000
