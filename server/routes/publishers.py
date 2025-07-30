from flask import jsonify, Response, Blueprint
from models import db, Publisher, Category

# Create a Blueprint for publishers routes
publishers_bp = Blueprint('publishers', __name__)

@publishers_bp.route('/api/publishers', methods=['GET'])
def get_publishers() -> Response:
    """Get all publishers with game count"""
    publishers = db.session.query(Publisher).all()
    publishers_list = [publisher.to_dict() for publisher in publishers]
    return jsonify(publishers_list)

@publishers_bp.route('/api/categories', methods=['GET'])
def get_categories() -> Response:
    """Get all categories with game count"""
    categories = db.session.query(Category).all()
    categories_list = [category.to_dict() for category in categories]
    return jsonify(categories_list)
