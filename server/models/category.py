"""
Category model for the Tailspin Toys crowdfunding platform.

This module defines the Category model class, which represents game categories
that help organize and classify games on the platform.
"""
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Category(BaseModel):
    """
    Model representing a game category on the crowdfunding platform.
    
    A category can have multiple games associated with it.
    Each category has a unique name and optional description.
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one category has many games
    games = relationship("Game", back_populates="category")
    
    @validates('name')
    def validate_name(self, key, name):
        """
        Validate the category name field.
        
        Args:
            key (str): The field name being validated
            name (str): The category name to validate
            
        Returns:
            str: The validated category name
            
        Raises:
            ValueError: If name doesn't meet validation requirements
        """
        return self.validate_string_length('Category name', name, min_length=2)
        
    @validates('description')
    def validate_description(self, key, description):
        """
        Validate the category description field.
        
        Args:
            key (str): The field name being validated
            description (str): The description to validate
            
        Returns:
            str | None: The validated description
            
        Raises:
            ValueError: If description doesn't meet validation requirements
        """
        return self.validate_string_length('Description', description, min_length=10, allow_none=True)
    
    def __repr__(self):
        """
        Return a string representation of the Category instance.
        
        Returns:
            str: A readable representation of the category
        """
        return f'<Category {self.name}>'
        
    def to_dict(self):
        """
        Convert the Category instance to a dictionary representation.
        
        Returns:
            dict: Dictionary containing category data including game count
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }