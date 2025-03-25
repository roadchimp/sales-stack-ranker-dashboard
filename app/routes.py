from flask import render_template, jsonify, request
from app import app, db

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sales-data')
def get_sales_data():
    # TODO: Implement actual sales data retrieval
    sample_data = {
        'sales': [
            {'name': 'Product A', 'value': 1000},
            {'name': 'Product B', 'value': 800},
            {'name': 'Product C', 'value': 600},
        ]
    }
    return jsonify(sample_data)

if __name__ == '__main__':
    app.run(debug=True) 