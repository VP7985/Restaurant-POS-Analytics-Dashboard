import sys
import os

# This allows Python to find the 'app' directory
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Runs the app in debug mode, accessible on your local network
    app.run(debug=True, host='0.0.0.0', port=5000)
