# ============================================================================
# APPLICATION ENTRY POINT AND SERVER CONFIGURATION
# ============================================================================
# This module serves as the main entry point for the Pythonic Flask application.
# It imports the configured Flask app instance and starts the development server.

# Import the configured Flask application instance from the pythonic package
# This instance includes all extensions, configurations, and routes
from pythonic import app


# ============================================================================
# DEVELOPMENT SERVER EXECUTION
# ============================================================================

# Main execution block - only runs when this file is executed directly
# This prevents the server from starting when the module is imported
if __name__ == "__main__":
    # Start the Flask development server with debug mode enabled
    # Debug mode provides detailed error pages and automatic reloading
    # Note: Debug mode should be disabled in production environments
    app.run(debug=True)