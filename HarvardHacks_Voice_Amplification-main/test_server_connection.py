#!/usr/bin/env python3
"""
Test script to verify server connection
"""

import requests
import time

def test_server():
    """Test if server is running and responding"""
    try:
        # Test if server is running
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("+ Server is running and responding")
            return True
        else:
            print(f"- Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("- Server is not running or not accessible")
        return False
    except Exception as e:
        print(f"- Error testing server: {e}")
        return False

if __name__ == "__main__":
    print("Testing server connection...")
    print("Make sure the server is running with: python start_server.py")
    print("=" * 50)
    
    # Wait a moment for server to start
    print("Waiting 3 seconds for server to start...")
    time.sleep(3)
    
    success = test_server()
    
    if success:
        print("\n[SUCCESS] Server is working!")
        print("Open your browser to: http://localhost:5000")
    else:
        print("\n[ERROR] Server is not working.")
        print("Try running: python start_server.py")
