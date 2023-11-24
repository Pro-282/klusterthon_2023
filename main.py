from app import create_app

app = create_app('development')  # || 'production', 'testing',

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # debug=True should only be used in development!
