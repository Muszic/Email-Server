from auth import signup, login

# Sign up a new user
signup("sangeet", "abc123")

# Try to log in
login("sangeet", "abc123")    # ✅ Should succeed
login("sangeet", "wrongpass") # ❌ Should fail

