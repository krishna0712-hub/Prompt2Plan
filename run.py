"""
run.py — Single entry point for Prompt2Plan
Usage:
  python run.py        # Build frontend & start server
  python run.py --test # Run backend test suite
"""
import subprocess
import sys
import os

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")


def run_tests():
    """Run pytest suite in backend/tests."""
    print("Running Prompt2Plan test suite...")
    res = subprocess.call([sys.executable, "-m", "pytest", "backend/tests", "-v"])
    sys.exit(res)


def build_frontend():
    """Build the React frontend to ensure dist/ has the latest UI/UX code."""
    print("[BUILD] Rebuilding frontend assets for latest UI/UX...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    
    if not os.path.isdir(os.path.join(FRONTEND_DIR, "node_modules")):
        print("  Running: npm install")
        subprocess.check_call([npm_cmd, "install"], cwd=FRONTEND_DIR)

    print("  Running: npm run build")
    subprocess.check_call([npm_cmd, "run", "build"], cwd=FRONTEND_DIR)

    print("[OK] Frontend built successfully")


def start_server():
    """Start the FastAPI server on port 8000."""
    print()
    print("=" * 50)
    print("  Prompt2Plan is running at http://localhost:8000")
    print("=" * 50)
    print()

    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    if "--test" in sys.argv or "test" in sys.argv:
        run_tests()

    try:
        build_frontend()
        start_server()
    except KeyboardInterrupt:
        print("\n\nShutting down Prompt2Plan...")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed: {e}")
        print("  Make sure Node.js and npm are installed.")
        sys.exit(1)
