import pytest
from unittest.mock import MagicMock, call
from sqlalchemy.exc import IntegrityError

from app.repository.user_repository import UserRepository
from app.domain.model.user import User

def test_get_by_id_returns_user():
    db = MagicMock()

    query = db.query.return_value
    query.filter.return_value.first.return_value = User(id=1, username="test")

    repo = UserRepository(db)

    result = repo.get_by_id(1)

    db.query.assert_called_once()
    query.filter.assert_called_once()
    assert result.username == "test"

def test_get_by_username_returns_user():
    db = MagicMock()

    query = db.query.return_value
    options = query.options.return_value
    options.filter.return_value.first.return_value = User(username="john")

    repo = UserRepository(db)

    result = repo.get_by_username("john")

    db.query.assert_called_once()
    query.options.assert_called_once()
    options.filter.assert_called_once()

    assert result.username == "john"

def test_save_user_success():
    db = MagicMock()
    user = User(username="john")

    repo = UserRepository(db)

    result = repo.save(user)

    db.add.assert_called_once_with(user)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(user)

    assert result == user

def test_save_user_integrity_error():
    db = MagicMock()

    user = User(username="john")

    db.commit.side_effect = IntegrityError("stmt", "params", "orig")

    repo = UserRepository(db)

    with pytest.raises(IntegrityError):
        repo.save(user)

    db.add.assert_called_once_with(user)
    db.rollback.assert_called_once()

def test_save_user_duplicate_username():
    db = MagicMock()

    user = User(username="john")

    class FakeIntegrityError(IntegrityError):
        def __init__(self):
            super().__init__("stmt", "params", None)
            self.orig = "user_username_key"

    db.commit.side_effect = FakeIntegrityError()

    repo = UserRepository(db)

    with pytest.raises(IntegrityError) as exc:
        repo.save(user)

    assert "user_username_key" in str(exc.value.orig)

    db.add.assert_called_once_with(user)
    db.rollback.assert_called_once()
    db.commit.assert_called_once()

def test_save_user_duplicate_email():
    db = MagicMock()

    user = User(username="john", email="john@test.com")

    class FakeIntegrityError(IntegrityError):
        def __init__(self):
            super().__init__("stmt", "params", None)
            self.orig = "user_email_key"

    db.commit.side_effect = FakeIntegrityError()

    repo = UserRepository(db)

    with pytest.raises(IntegrityError) as exc:
        repo.save(user)

    assert "user_email_key" in str(exc.value.orig)

    db.add.assert_called_once_with(user)
    db.rollback.assert_called_once()
    db.commit.assert_called_once()
