# Test payloads for comments app tests

CREATE_COMMENT_PAYLOAD = {
    "content": "This is a test comment created during testing"
}

CREATE_REPLY_PAYLOAD = {
    "content": "This is a test reply created during testing",
    "parent_uid": None  # This will be set dynamically in the tests
}

UPDATE_COMMENT_PAYLOAD = {
    "content": "This is an updated comment content"
}