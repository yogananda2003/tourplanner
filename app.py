from flask import Flask, render_template, request, jsonify
# Import the core function from your logic file
from tourism_system4 import run_tourism_system 

app = Flask(__name__)

# Route for the homepage (serving the HTML form)
@app.route('/')
def index():
    """Serves the main HTML page for user input."""
    return render_template('index.html')

# Route to handle the AJAX request from the frontend
@app.route('/api/query', methods=['POST'])
def query_system():
    """Receives the user's query and calls the multi-agent system."""
    
    # 1. Get user input from the AJAX request
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({'message': 'Please enter a query.', 'status': 'Error'}), 400

    # 2. Call the core logic function
    # Note: run_tourism_system returns a dictionary with 'message' and 'status'
    result = run_tourism_system(user_query)
    
    # 3. Return the result as a JSON response to the frontend
    return jsonify(result)

if __name__ == '__main__':
    # Flask will run on http://127.0.0.1:5000/
    app.run(debug=True)