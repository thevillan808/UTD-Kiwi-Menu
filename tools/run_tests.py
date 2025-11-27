#!/usr/bin/env python3
"""
Simple test runner for UTD Kiwi CLI.
"""

import subprocess
import sys
import os

def main():
    """Run the comprehensive test suite."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(script_dir, 'test_comprehensive.py')
    
    print("Running UTD Kiwi CLI Test Suite...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              cwd=script_dir, 
                              capture_output=False)
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)