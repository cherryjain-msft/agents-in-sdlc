from flask import jsonify, Response, Blueprint, request
from models import db, Game, Publisher, Category
from sqlalchemy.orm import Query
from typing import Optional, Dict, Any
import math

# Create a Blueprint for games routes
games_bp = Blueprint('games', __name__)

def get_games_base_query() -> Query:
    return db.session.query(Game).join(
        Publisher, 
        Game.publisher_id == Publisher.id, 
        isouter=True
    ).join(
        Category, 
        Game.category_id == Category.id, 
        isouter=True
    )

@games_bp.route('/api/games', methods=['GET'])
def get_games() -> Response:
    # Get filter parameters from query string
    category_id: Optional[str] = request.args.get('category_id')
    publisher_id: Optional[str] = request.args.get('publisher_id')
    
    # Get pagination parameters from query string
    page: int = int(request.args.get('page', 1))
    limit: int = int(request.args.get('limit', 20))
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:  # Max 100 items per page for performance
        limit = 20
    
    # Start with base query
    games_query = get_games_base_query()
    
    # Apply filters if provided
    if category_id and category_id.isdigit():
        games_query = games_query.filter(Game.category_id == int(category_id))
    
    if publisher_id and publisher_id.isdigit():
        games_query = games_query.filter(Game.publisher_id == int(publisher_id))
    
    # Get total count before applying pagination
    total_items: int = games_query.count()
    
    # Calculate pagination metadata
    total_pages: int = math.ceil(total_items / limit) if total_items > 0 else 1
    offset: int = (page - 1) * limit
    
    # Apply pagination
    games_result = games_query.offset(offset).limit(limit).all()
    
    # Convert the results using the model's to_dict method
    games_list = [game.to_dict() for game in games_result]
    
    # Create paginated response with metadata
    response_data: Dict[str, Any] = {
        'games': games_list,
        'pagination': {
            'current_page': page,
            'total_pages': total_pages,
            'total_items': total_items,
            'items_per_page': limit,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return jsonify(response_data)

@games_bp.route('/api/games/<int:id>', methods=['GET'])
def get_game(id: int) -> tuple[Response, int] | Response:
    # Use the base query and add filter for specific game
    game_query = get_games_base_query().filter(Game.id == id).first()
    
    # Return 404 if game not found
    if not game_query: 
        return jsonify({"error": "Game not found"}), 404
    
    # Convert the result using the model's to_dict method
    game = game_query.to_dict()
    
    return jsonify(game)
