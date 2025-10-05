#!/usr/bin/env python3
"""
Startup script for the Voice Amplification server
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("Voice Amplification Server")
    print("=" * 60)
    print("Starting server...")
    print("Open your browser to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        from server import app, socketio
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
    except Exception as e:
        print(f"\nError starting server: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main()
