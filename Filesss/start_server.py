"""
Start a local web server to serve the HTML viewer
Tries multiple ports until it finds an available one
"""

import http.server
import socketserver
import webbrowser
import sys
from pathlib import Path
import socket


def is_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False


def find_available_port(start_port=9000, max_attempts=100):
    """Find an available port starting from start_port"""
    print(f"[INFO] Checking ports starting from {start_port}...")
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            print(f"[OK] Port {port} is available")
            return port
        else:
            if port < start_port + 5:  # Only show first few attempts
                print(f"[SKIP] Port {port} is in use, trying next...")
    print(f"[ERROR] No available port found after {max_attempts} attempts")
    return None


def get_port_from_registry():
    """Get port from registry, with fallback to dynamic search"""
    import sys
    from pathlib import Path
    
    # Add infrastructure directory to path
    workspace_root = Path(__file__).parent.parent
    infrastructure_path = workspace_root / "infrastructure"
    
    if infrastructure_path.exists():
        sys.path.insert(0, str(infrastructure_path))
        try:
            from port_utils import get_port, validate_port_assignment
            
            port = get_port("agentic-coding-workflow", "viewer")
            if port:
                # Validate but allow fallback for dev-only servers
                is_valid, error_msg = validate_port_assignment("agentic-coding-workflow", "viewer")
                if is_valid:
                    return port
                else:
                    print(f"[WARN] Registry port {port} unavailable: {error_msg}")
                    print("[INFO] Falling back to dynamic port search in dev-only range (9000-9099)")
        except Exception as e:
            print(f"[WARN] Could not load port from registry: {e}")
            print("[INFO] Falling back to dynamic port search in dev-only range (9000-9099)")
    
    return None


def start_server(port, directory):
    """Start HTTP server on specified port"""
    import os
    os.chdir(directory)
    
    handler = http.server.SimpleHTTPRequestHandler
    
    # Add CORS headers to allow local file access
    class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
            print(f"[SUCCESS] Server started on http://localhost:{port}")
            print(f"[INFO] Serving directory: {directory}")
            print(f"[INFO] Opening browser...")
            print(f"[INFO] Press Ctrl+C to stop the server\n")
            
            # Open browser
            url = f"http://localhost:{port}/latest_viewer.html"
            webbrowser.open(url)
            
            # Serve forever
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False


def main():
    """Main function"""
    import os
    
    # Get the output directory
    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"
    
    if not output_dir.exists():
        print("[ERROR] Output directory not found. Please run the workflow first.")
        sys.exit(1)
    
    html_file = output_dir / "latest_viewer.html"
    if not html_file.exists():
        print("[ERROR] HTML viewer not found. Generating...")
        # Try to generate it
        try:
            from generate_html_viewer import main as generate_viewer
            generate_viewer()
        except Exception as e:
            print(f"[ERROR] Failed to generate HTML viewer: {e}")
            sys.exit(1)
    
    # Get port from registry or find available port in dev-only range
    print("[INFO] Looking for available port...")
    
    # Try registry first
    port = get_port_from_registry()
    
    # If registry port unavailable or not found, search in dev-only range
    if port is None:
        port = find_available_port(start_port=9000, max_attempts=100)
    
    if port is None:
        print("[ERROR] Could not find an available port after 100 attempts")
        print("[ERROR] Tried dev-only range 9000-9099")
        sys.exit(1)
    
    print(f"[INFO] Using port: {port}")
    
    # Start server
    start_server(port, str(output_dir))


if __name__ == "__main__":
    main()
