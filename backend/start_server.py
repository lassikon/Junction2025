#!/usr/bin/env python3
"""
Quick start script for LifeSim backend development.
Runs the FastAPI server with auto-reload.
"""

import subprocess
import sys
import os


def main():
    """Start the FastAPI server"""
    print("🚀 Starting LifeSim Backend Server...")
    print()
    print("Server will be available at:")
    print("  - API: http://localhost:8000")
    print("  - Docs: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print()
    print("Press Ctrl+C to stop the server")
    print()

    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)

    try:
        # Run uvicorn with auto-reload
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
