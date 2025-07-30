# filepath: server/models/base.py
"""
Base model class providing common functionality for all database models.

This module defines the BaseModel class that serves as a foundation
for all SQLAlchemy models in the application.
"""
from . import db

class BaseModel(db.Model):
    """
    Abstract base model class providing common functionality for all models.
    
    This class includes validation methods and other shared functionality
    that can be used by all model classes in the application.
    """
    __abstract__ = True
    
    @staticmethod
    def validate_string_length(field_name, value, min_length=2, allow_none=False):
        """
        Validate that a string field meets minimum length requirements.
        
        Args:
            field_name (str): The name of the field being validated (for error messages)
            value (str | None): The string value to validate
            min_length (int, optional): Minimum required length. Defaults to 2.
            allow_none (bool, optional): Whether None values are allowed. Defaults to False.
            
        Returns:
            str | None: The validated string value
            
        Raises:
            ValueError: If the value doesn't meet validation requirements
        """
        if value is None:
            if allow_none:
                return value
            else:
                raise ValueError(f"{field_name} cannot be empty")
        
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
            
        if len(value.strip()) < min_length:
            raise ValueError(f"{field_name} must be at least {min_length} characters")
            
        return value