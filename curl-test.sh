#!/usr/bin/env bash

set -e

API_URL="http://127.0.0.1:5000/api/timeline_post"

RANDOM_ID="$(date +%s)-$RANDOM"
TEST_NAME="Curl Test User"
TEST_EMAIL="curl-test-${RANDOM_ID}@example.com"
TEST_CONTENT="Random timeline post ${RANDOM_ID}"

echo "Creating a random timeline post..."

POST_RESPONSE=$(curl -s -X POST "$API_URL" \
  -d "name=$TEST_NAME" \
  -d "email=$TEST_EMAIL" \
  -d "content=$TEST_CONTENT")

echo "POST response:"
echo "$POST_RESPONSE"
echo

if echo "$POST_RESPONSE" | grep -q "$TEST_CONTENT"; then
  echo "POST test passed: timeline post was created."
else
  echo "POST test failed: expected content was not returned."
  exit 1
fi

echo
echo "Retrieving timeline posts..."

GET_RESPONSE=$(curl -s -X GET "$API_URL")

echo "GET response:"
echo "$GET_RESPONSE"
echo

if echo "$GET_RESPONSE" | grep -q "$TEST_CONTENT"; then
  echo "GET test passed: the new timeline post was found."
else
  echo "GET test failed: the new timeline post was not found."
  exit 1
fi

echo
echo "All timeline endpoint tests passed."