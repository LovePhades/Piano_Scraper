from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def run_scraper():
    result = subprocess.run(['python3', 'scraper.py'], capture_output=True, text=True)
    return jsonify({
        'status': 'Scraper executed successfully!',
        'output': result.stdout,
        'errors': result.stderr
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)

