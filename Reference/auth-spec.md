# Authentication Specification: Modular Streamlit Google OAuth

## Overview

This specification defines how to implement Streamlit's built-in Google OAuth authentication using a modular architecture that allows developers to enable or disable authentication based on environment configuration while preserving the exact same user experience and functionality.

## Design Principles

### 1. **Preserve Native Streamlit Behavior**
- Use only Streamlit's built-in authentication methods (`st.user`, `st.login()`, `st.logout()`)
- Maintain identical user interface and experience
- No custom authentication libraries or external dependencies
- Preserve all existing OAuth flow and session handling

### 2. **Modular Architecture**
- Separate authentication logic from application entry point
- Create reusable components for authentication UI
- Centralize authentication state management
- Enable easy testing and maintenance

### 3. **Configuration-Driven**
- Environment variable controls authentication state
- Default to production-ready (authentication enabled)
- Allow development mode without OAuth setup
- Runtime configuration without code changes

### 4. **Backward Compatibility**
- No breaking changes to existing functionality
- Seamless migration from inline authentication code
- Preserve all existing session state and user flows

## Architecture Components

### Component 1: Authentication UI Components (`src/components/auth_components.py`)

**Purpose**: Encapsulate all authentication-related UI components while preserving exact Streamlit behavior.

```python
def render_login_screen():
    """
    Render the login screen with Google OAuth integration.
    
    This preserves the exact same UI and behavior as inline implementation,
    using Streamlit's built-in Google OAuth functionality.
    """
    st.title("🔒 Authentication Required")
    st.markdown("Please authenticate with Google to access [App Name]")
    
    # Native Streamlit OAuth - no custom libraries
    st.button("Login with Google", on_click=st.login)
    
    st.markdown("---")
    st.info("After logging in, you'll be redirected back to the app automatically.")
    
    # Stop execution until user is authenticated
    st.stop()

def render_logout_button():
    """
    Render logout button for sidebar.
    
    Preserves exact logout functionality using Streamlit's built-in methods.
    """
    if st.button("🚪 Logout", use_container_width=True):
        st.logout()

def is_user_logged_in() -> bool:
    """
    Check if user is currently logged in using Streamlit's built-in user object.
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    try:
        return hasattr(st, 'user') and st.user.is_logged_in
    except AttributeError:
        # Handle case when running outside Streamlit context (e.g., tests)
        return False
```

**Key Features**:
- ✅ Uses only `st.login()`, `st.logout()`, `st.user.is_logged_in`
- ✅ Identical UI/UX to inline implementation
- ✅ Graceful error handling for non-Streamlit contexts
- ✅ Reusable across multiple pages if needed

### Component 2: Authentication Service (`src/services/auth_service.py`)

**Purpose**: Centralize authentication logic and provide configuration-based control.

```python
import os
from src.components.auth_components import render_login_screen, is_user_logged_in

def is_authentication_enabled() -> bool:
    """
    Check if authentication is enabled based on environment configuration.
    
    Returns:
        bool: True if authentication is enabled, False otherwise
    """
    return os.getenv("AUTH_ENABLED", "true").lower() == "true"

def is_authentication_required() -> bool:
    """
    Check if authentication is required for the current user.
    
    Authentication is required when:
    1. Authentication is enabled (AUTH_ENABLED=true)
    2. AND user is not logged in (not st.user.is_logged_in)
    
    Returns:
        bool: True if authentication is required, False otherwise
    """
    if not is_authentication_enabled():
        return False
    
    return not is_user_logged_in()

def handle_authentication():
    """
    Handle the authentication flow.
    
    This preserves the exact same behavior as inline implementation:
    - If authentication is required, render login screen and stop execution
    - If authentication is disabled or user is logged in, continue normally
    """
    if is_authentication_required():
        render_login_screen()  # This will call st.stop() internally

def get_authentication_status() -> dict:
    """
    Get current authentication status information for debugging.
    
    Returns:
        dict: Authentication status with keys:
            - enabled: Whether authentication is enabled
            - required: Whether authentication is currently required
            - logged_in: Whether user is currently logged in
    """
    return {
        "enabled": is_authentication_enabled(),
        "required": is_authentication_required(),
        "logged_in": is_user_logged_in()
    }
```

**Key Features**:
- ✅ Configuration-driven authentication control
- ✅ Preserves exact same authentication logic flow
- ✅ Provides debugging and status information
- ✅ No dependencies on external authentication libraries

### Component 3: Configuration System (`src/core/config.py`)

**Purpose**: Centralize configuration constants including authentication settings.

```python
import os

# Authentication configuration
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "true").lower() == "true"

# Other existing configuration constants...
```

**Key Features**:
- ✅ Environment variable driven
- ✅ Defaults to production-ready (enabled)
- ✅ Centralized with other app configuration
- ✅ Boolean conversion for easy usage

### Component 4: Application Integration (`app.py`)

**Purpose**: Clean integration of modular authentication into main application.

```python
# Before (inline implementation)
if not st.user.is_logged_in:
    st.title("🔒 Authentication Required")
    st.markdown("Please authenticate with Google to access Finance Bro")
    st.button("Login with Google", on_click=st.login)
    st.markdown("---")
    st.info("After logging in, you'll be redirected back to the app automatically.")
    st.stop()

# After (modular implementation)
from src.services.auth_service import handle_authentication
handle_authentication()

# Sidebar logout - Before
if st.button("🚪 Logout", use_container_width=True):
    st.logout()

# Sidebar logout - After
from src.components.auth_components import render_logout_button
render_logout_button()
```

**Key Features**:
- ✅ Identical behavior to inline implementation
- ✅ Cleaner, more maintainable code
- ✅ Single line replacement for complex authentication logic
- ✅ No changes to user experience

## Configuration Specification

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AUTH_ENABLED` | boolean | `true` | Enable/disable Google OAuth authentication |

### Configuration Behavior

#### Production Mode (Default)
```bash
AUTH_ENABLED=true  # or omit entirely
```
- ✅ Full Google OAuth authentication required
- ✅ Users must authenticate to access application
- ✅ Uses `.streamlit/secrets.toml` for OAuth configuration
- ✅ Identical behavior to non-modular implementation

#### Development Mode
```bash
AUTH_ENABLED=false
```
- ✅ Authentication bypassed completely
- ✅ No Google OAuth setup required
- ✅ Direct access to application
- ✅ Useful for local development and testing

### Environment Configuration Files

#### `.env.example`
```bash
# Authentication Configuration
# Set to "false" to disable Google OAuth for development
AUTH_ENABLED=true

# Other environment variables...
OPENAI_API_KEY=your_openai_api_key_here
```

#### `.streamlit/secrets.toml` (unchanged)
```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-very-long-random-cookie-secret-string"
client_id = "your-google-client-id.apps.googleusercontent.com"
client_secret = "your-google-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

## Implementation Guide

### Step 1: Create Authentication Components

1. **Create** `src/components/auth_components.py`
   - Implement `render_login_screen()`
   - Implement `render_logout_button()`
   - Implement `is_user_logged_in()`
   - Add error handling for non-Streamlit contexts

2. **Test** components in isolation
   - Verify UI matches original implementation
   - Test error handling outside Streamlit context

### Step 2: Create Authentication Service

1. **Create** `src/services/auth_service.py`
   - Implement configuration reading logic
   - Implement authentication flow control
   - Add status and debugging functions

2. **Test** service functionality
   - Test with `AUTH_ENABLED=true` and `AUTH_ENABLED=false`
   - Verify identical logic flow to original implementation

### Step 3: Update Configuration

1. **Modify** `src/core/config.py`
   - Add `AUTH_ENABLED` configuration constant
   - Import required `os` module

2. **Update** `.env.example`
   - Add `AUTH_ENABLED` example configuration
   - Document usage for development vs production

### Step 4: Integrate with Application

1. **Modify** main application file (`app.py`)
   - Import authentication service and components
   - Replace inline authentication code with service calls
   - Test that behavior is identical

2. **Verify** no breaking changes
   - All existing functionality preserved
   - User experience unchanged
   - Session state handling intact

### Step 5: Testing and Validation

1. **Test** production mode (`AUTH_ENABLED=true`)
   - Verify Google OAuth works identically
   - Test login/logout flow
   - Verify all existing functionality

2. **Test** development mode (`AUTH_ENABLED=false`)
   - Verify authentication is bypassed
   - Test direct application access
   - Verify all application features work without auth

3. **Test** edge cases
   - Invalid environment variable values
   - Missing environment variables
   - Non-Streamlit execution contexts

## Security Considerations

### 1. **Default Secure Configuration**
- `AUTH_ENABLED` defaults to `true` (secure by default)
- Production deployments automatically have authentication enabled
- Development mode requires explicit opt-out

### 2. **No Security Compromise**
- Uses only Streamlit's built-in authentication mechanisms
- No custom authentication code that could introduce vulnerabilities
- Preserves all existing security features of Streamlit OAuth

### 3. **Environment Variable Security**
- `AUTH_ENABLED` is a public configuration variable (not secret)
- Actual authentication secrets remain in `.streamlit/secrets.toml`
- No sensitive information exposed in environment configuration

### 4. **Development vs Production**
- Clear separation between development and production modes
- Development mode only suitable for local development
- Production deployment instructions emphasize authentication requirements

## Testing Strategy

### Unit Testing

```python
def test_authentication_enabled_true():
    os.environ["AUTH_ENABLED"] = "true"
    assert is_authentication_enabled() == True

def test_authentication_enabled_false():
    os.environ["AUTH_ENABLED"] = "false"
    assert is_authentication_enabled() == False

def test_authentication_enabled_default():
    if "AUTH_ENABLED" in os.environ:
        del os.environ["AUTH_ENABLED"]
    assert is_authentication_enabled() == True  # Default is enabled

def test_user_logged_in_outside_streamlit():
    # Test graceful handling when not in Streamlit context
    result = is_user_logged_in()
    assert isinstance(result, bool)
```

### Integration Testing

1. **Test** with actual Streamlit application
2. **Verify** authentication flow in both modes
3. **Test** session persistence and logout functionality
4. **Validate** no breaking changes to existing features

## Migration Guide

### From Inline Authentication

**Before:**
```python
# app.py
if not st.user.is_logged_in:
    st.title("🔒 Authentication Required")
    # ... authentication UI code ...
    st.stop()

# Sidebar
if st.button("🚪 Logout", use_container_width=True):
    st.logout()
```

**After:**
```python
# app.py
from src.services.auth_service import handle_authentication
from src.components.auth_components import render_logout_button

handle_authentication()

# Sidebar
render_logout_button()
```

### Migration Steps

1. **Create** modular authentication components following this specification
2. **Test** components preserve identical behavior
3. **Replace** inline authentication code with service calls
4. **Test** full application functionality
5. **Add** environment variable configuration
6. **Document** new configuration options

## Best Practices

### 1. **Development Workflow**
- Use `AUTH_ENABLED=false` for local development
- Use `AUTH_ENABLED=true` for staging and production
- Document authentication requirements in README

### 2. **Code Organization**
- Keep authentication UI components separate from business logic
- Centralize authentication configuration in core config
- Use descriptive function names that indicate preservation of original behavior

### 3. **Error Handling**
- Handle non-Streamlit execution contexts gracefully
- Provide clear error messages for configuration issues
- Maintain compatibility with testing frameworks

### 4. **Documentation**
- Document environment variable configuration
- Provide examples for both development and production modes
- Include migration guide for existing applications

## Troubleshooting

### Common Issues

1. **"st.user has no attribute 'is_logged_in'"**
   - **Cause**: Running outside Streamlit context
   - **Solution**: Ensure `is_user_logged_in()` has try-catch for AttributeError

2. **Authentication always enabled despite AUTH_ENABLED=false**
   - **Cause**: Environment variable not loaded or case sensitivity
   - **Solution**: Verify `.env` file loading and lowercase string comparison

3. **OAuth configuration errors**
   - **Cause**: Missing or incorrect `.streamlit/secrets.toml`
   - **Solution**: Verify Google OAuth setup and secrets configuration

### Debug Information

Use `get_authentication_status()` for debugging:

```python
from src.services.auth_service import get_authentication_status
status = get_authentication_status()
print(f"Auth Status: {status}")
# Output: {'enabled': True, 'required': False, 'logged_in': True}
```

## Conclusion

This specification provides a complete guide for implementing modular Streamlit Google OAuth authentication that:

- ✅ **Preserves** exact same Streamlit built-in authentication behavior
- ✅ **Enables** development/production configuration flexibility
- ✅ **Maintains** backward compatibility and user experience
- ✅ **Provides** clean, maintainable, and testable code architecture
- ✅ **Follows** security best practices and proper error handling

The modular approach allows developers to easily toggle authentication for different environments while maintaining the robust, secure OAuth implementation that Streamlit provides out of the box.