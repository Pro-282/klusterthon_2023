from flask import Flask, jsonify, Blueprint

health_blueprint = Blueprint('health', __name__)

@health_blueprint.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "API is live"}), 200