from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/confirm', methods=['POST'])
def confirm_event():
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'Missing event data'}), 400
        
        # Just echo back the data for testing
        return jsonify({
            'status': 'success', 
            'message': 'Event received (test server)',
            'event': data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("Starting simple test server on http://127.0.0.1:5000")
    print("Use Ctrl+C to stop the server")
    app.run(port=5000, debug=True)
