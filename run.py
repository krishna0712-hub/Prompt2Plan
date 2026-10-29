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
    index_file = os.path.join(DIST_DIR, "index.html")
    if os.path.isfile(index_file) and not os.environ.get("FORCE_FRONTEND_BUILD"):
        print("[INFO] Pre-built frontend assets found in frontend/dist. Skipping build.")
        return

    print("[BUILD] Rebuilding frontend assets for latest UI/UX...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    
    try:
        if not os.path.isdir(os.path.join(FRONTEND_DIR, "node_modules")):
            print("  Running: npm install")
            subprocess.check_call([npm_cmd, "install"], cwd=FRONTEND_DIR)

        print("  Running: npm run build")
        subprocess.check_call([npm_cmd, "run", "build"], cwd=FRONTEND_DIR)
        print("[OK] Frontend built successfully")
    except Exception as e:
        if os.path.isfile(index_file):
            print(f"[WARN] npm build failed ({e}), using existing frontend/dist assets.")
        else:
            raise


def start_server():
    """Start the FastAPI server on port (defaults to PORT env var or 8000)."""
    port = int(os.environ.get("PORT", 8000))
    print()
    print("=" * 50)
    print(f"  Prompt2Plan is running at http://0.0.0.0:{port}")
    print("=" * 50)
    print()

    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
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
    except Exception as e:
        print(f"\n[ERROR] Startup failed: {e}")
        sys.exit(1)
