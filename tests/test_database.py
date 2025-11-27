"""
Tests for database operations.

Tests user CRUD operations, authentication, and admin protection.
"""

import pytest
from app import db_sqlalchemy as db
from app.domain.User import User
from app.exceptions import (
    UniqueConstraintError,
    UserNotFoundException,
    AdminProtectionException,
    InvalidCredentialsException,
    ValidationException
)


class TestUserOperations:
    """Test user database operations"""
    
    def test_create_user(self, test_db):
        """Test creating a new user"""
        user = User("newuser", "password", "New", "User", 500.0, "user")
        db.create_new_user(user)
        
        retrieved = db.query_user("newuser")
        assert retrieved is not None
        assert retrieved.username == "newuser"
        assert retrieved.first_name == "New"
        assert retrieved.last_name == "User"
        assert retrieved.balance == 500.0
        assert retrieved.role == "user"
    
    def test_create_duplicate_user(self, test_db, sample_user):
        """Test that creating duplicate user raises error"""
        user = User("testuser", "password", "Duplicate", "User", 100.0, "user")
        
        with pytest.raises(UniqueConstraintError):
            db.create_new_user(user)
    
    def test_query_user(self, test_db, sample_user):
        """Test querying user by username"""
        user = db.query_user("testuser")
        assert user is not None
        assert user.username == "testuser"
    
    def test_query_nonexistent_user(self, test_db):
        """Test querying nonexistent user returns None"""
        user = db.query_user("nonexistent")
        assert user is None
    
    def test_query_all_users(self, test_db, sample_user, sample_admin):
        """Test querying all users"""
        users = db.query_all_users()
        assert len(users) >= 2
        usernames = [u.username for u in users]
        assert "testuser" in usernames
        assert "admin" in usernames
    
    def test_delete_user(self, test_db, sample_user, sample_admin):
        """Test deleting a user"""
        success = db.delete_user("testuser")
        assert success is True
        
        user = db.query_user("testuser")
        assert user is None
    
    def test_delete_nonexistent_user(self, test_db):
        """Test deleting nonexistent user raises error"""
        with pytest.raises(UserNotFoundException):
            db.delete_user("nonexistent")
    
    def test_delete_last_admin_protected(self, test_db, sample_admin):
        """Test that deleting last admin is prevented"""
        with pytest.raises(AdminProtectionException):
            db.delete_user("admin")
    
    def test_update_user_role(self, test_db, sample_user):
        """Test updating user role"""
        success = db.update_user_role("testuser", "admin")
        assert success is True
        
        user = db.query_user("testuser")
        assert user.role == "admin"
    
    def test_update_user_balance(self, test_db, sample_user):
        """Test updating user balance"""
        success = db.update_user_balance("testuser", 2000.0)
        assert success is True
        
        user = db.query_user("testuser")
        assert user.balance == 2000.0


class TestAuthentication:
    """Test authentication operations"""
    
    def test_authenticate_valid_credentials(self, test_db, sample_user):
        """Test authentication with valid credentials"""
        user = db.authenticate("testuser", "password123")
        assert user is not None
        assert user.username == "testuser"
    
    def test_authenticate_invalid_password(self, test_db, sample_user):
        """Test authentication with invalid password"""
        with pytest.raises(InvalidCredentialsException):
            db.authenticate("testuser", "wrongpassword")
    
    def test_authenticate_nonexistent_user(self, test_db):
        """Test authentication with nonexistent user"""
        with pytest.raises(InvalidCredentialsException):
            db.authenticate("nonexistent", "password")
    
    def test_authenticate_empty_username(self, test_db):
        """Test authentication with empty username"""
        with pytest.raises(ValidationException):
            db.authenticate("", "password")
    
    def test_authenticate_empty_password(self, test_db, sample_user):
        """Test authentication with empty password"""
        with pytest.raises(ValidationException):
            db.authenticate("testuser", "")


class TestSessionManagement:
    """Test session management"""
    
    def test_get_current_user_initial(self):
        """Test getting current user initially returns None"""
        user = db.get_current_user()
        assert user is None
    
    def test_set_and_get_current_user(self, test_db, sample_user):
        """Test setting and getting current user"""
        user = db.query_user("testuser")
        db.set_current_user(user)
        
        current = db.get_current_user()
        assert current is not None
        assert current.username == "testuser"
        
        # Cleanup
        db.set_current_user(None)
    
    def test_clear_current_user(self, test_db, sample_user):
        """Test clearing current user"""
        user = db.query_user("testuser")
        db.set_current_user(user)
        
        db.set_current_user(None)
        current = db.get_current_user()
        assert current is None
