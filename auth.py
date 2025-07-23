from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Return a Werkzeug scrypt hash of the password."""
    return generate_password_hash(password, method="scrypt")

def verify_password(stored_hash: str, provided_password: str) -> bool:
    """Check the provided password against the stored hash."""
    return check_password_hash(stored_hash, provided_password)