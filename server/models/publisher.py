"""
Publisher model for the Tailspin Toys crowdfunding platform.

This module defines the Publisher model class, which represents game publishers
that publish games seeking crowdfunding support.
"""
from . import db
from .base import BaseModel
from sqlalchemy.orm import validates, relationship

class Publisher(BaseModel):
    """
    Model representing a game publisher on the crowdfunding platform.
    
    A publisher can have multiple games associated with them.
    Each publisher has a unique name and optional description.
    """
    __tablename__ = 'publishers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # One-to-many relationship: one publisher has many games
    games = relationship("Game", back_populates="publisher")

    @validates('name')
    def validate_name(self, key, name):
        """
        Validate the publisher name field.
        
        Args:
            key (str): The field name being validated
            name (str): The publisher name to validate
            
        Returns:
            str: The validated publisher name
            
        Raises:
            ValueError: If name doesn't meet validation requirements
        """
        return self.validate_string_length('Publisher name', name, min_length=2)

    @validates('description')
    def validate_description(self, key, description):
        """
        Validate the publisher description field.
        
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
        Return a string representation of the Publisher instance.
        
        Returns:
            str: A readable representation of the publisher
        """
        return f'<Publisher {self.name}>'

    def to_dict(self):
        """
        Convert the Publisher instance to a dictionary representation.
        
        Returns:
            dict: Dictionary containing publisher data including game count
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'game_count': len(self.games) if self.games else 0
        }