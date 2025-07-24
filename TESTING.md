# Testing Documentation

## Recent Changes

### Test File Refactoring

We've refactored several large test files into smaller, more focused files to improve maintainability:

1. **Core App Tests**:
   - Split `test_core.py` (553 lines) into:
     - `test_basic_views.py`: Tests for HomeView and HealthCheckView
     - `test_follow.py`: Tests for FollowModel and FollowToggleView
     - `test_collections.py`: Tests for CollectionListCreateView and CollectionDetailView
     - `test_collection_members.py`: Tests for CollectionMemberView
     - `test_collection_posts.py`: Tests for CollectionAddPostView and DefaultCollectionAddPostView

2. **Posts App Tests**:
   - Split `test_posts.py` (291 lines) into:
     - `test_post_list_create.py`: Tests for PostListCreateView
     - `test_post_detail.py`: Tests for PostDetailView
   - Added JWT client fixtures to `conftest.py`

All tests continue to pass after refactoring, and test coverage has been maintained.

## Current Test Coverage

| App | View File | Coverage | Missing Lines |
|-----|-----------|----------|--------------|
| Core | views.py | 100% | None |
| Comments | views.py | 91% | 90-104, 134 |
| Notifications | views.py | 93% | 17 |
| Posts | views.py | 84% | 170-189 |
| Likes | views.py | 73% | 44-58 |
| Users | views.py | 66% | 60-63, 97-112, 179, 190-197, 211-212, 228-238, 265-282 |

## Recommendations

1. **Maintain Small, Focused Test Files**:
   - Keep test files under 200 lines when possible
   - Group tests by functionality or endpoint
   - Use descriptive test class and method names

2. **Improve Test Coverage**:
   - Focus on increasing coverage for `users/views.py` (66%) and `likes/views.py` (73%)
   - Add tests for edge cases and error conditions
   - Use pytest fixtures to reduce test setup duplication

3. **Test Organization**:
   - Use `conftest.py` for shared fixtures
   - Group related tests in the same file
   - Follow a consistent naming convention for test files and test methods

4. **Test Maintenance**:
   - Update tests when modifying view functionality
   - Run coverage reports regularly to identify gaps
   - Consider adding test coverage checks to CI/CD pipeline

## Running Tests

To run all tests:
```bash
python -m pytest
```

To run tests with coverage:
```bash
python -m pytest --cov=snapsapi.apps.comments.views --cov=snapsapi.apps.core.views --cov=snapsapi.apps.likes.views --cov=snapsapi.apps.notifications.views --cov=snapsapi.apps.posts.views --cov=snapsapi.apps.users.views --cov-report=term-missing
```

To run specific test files:
```bash
python -m pytest snapsapi/apps/core/tests/test_basic_views.py
```