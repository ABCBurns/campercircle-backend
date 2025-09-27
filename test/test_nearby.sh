#!/bin/bash

BASE_URL="http://localhost:8000"

# -------------------------------
# Helper function to register & login a user
# -------------------------------
register_and_login() {
  EMAIL=$1
  PASSWORD=$2

  # Register (ignore errors if user already exists)
  curl -s -X POST "$BASE_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\", \"password\":\"$PASSWORD\"}" >/dev/null

  # Login
  TOKEN=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$EMAIL&password=$PASSWORD" \
    | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

  echo $TOKEN
}

# -------------------------------
# Register & login users
# -------------------------------
TOKEN1=$(register_and_login "user4@example.com" "password123")
TOKEN2=$(register_and_login "user5@example.com" "password123")
TOKEN3=$(register_and_login "user6@example.com" "password123")

echo $TOKEN1
echo $TOKEN2
echo $TOKEN3

# -------------------------------
# Set locations
# -------------------------------
curl -s -X POST "$BASE_URL/users/location?lat=48.8566&lon=2.3522" \
  -H "Authorization: Bearer $TOKEN1"

curl -s -X POST "$BASE_URL/users/location?lat=48.8570&lon=2.3530" \
  -H "Authorization: Bearer $TOKEN2"

curl -s -X POST "$BASE_URL/users/location?lat=48.9000&lon=2.4000" \
  -H "Authorization: Bearer $TOKEN3"

# -------------------------------
# Test nearby endpoint for user1
# -------------------------------
echo "Nearby users for user1 within 5 km:"
curl -s -X GET "$BASE_URL/users/nearby?radius_km=50" \
  -H "Authorization: Bearer $TOKEN1"
echo
