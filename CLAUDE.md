# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A grocery list application with smart features including item suggestions, price tracking via Kroger API, and store location search. Built with React frontend and Python Flask backend using SQLite.

## Development Commands

### Backend (Flask)
```bash
cd grocery_backend
# Activate virtual environment
..\.venv\Scripts\activate  # Windows
# Run the server (starts on port 5000 by default)
python main.py
```

### Frontend (React)
```bash
cd grocery_frontend
npm start    # Development server on port 3000
npm test     # Run tests
npm run build  # Production build
```

## Architecture

### Backend Structure (`grocery_backend/`)
- **`__init__.py`**: Flask app factory with CORS configuration and blueprint registration
- **`main.py`**: Entry point, initializes database tables and runs the app
- **`config.py`**: Configuration variables (DB_PATH, API keys, STORE_ID) - gitignored
- **`routes/`**: Flask blueprints for API endpoints
  - `items.py`: CRUD for grocery list items (`/api/items`)
  - `previous.py`: Recently purchased items (`/api/previous`)
  - `suggestions.py`: Smart suggestions with sale detection (`/api/suggestions`)
  - `auth.py`: User registration and login (`/api/auth`)
  - `locations.py`: Store location search by zipcode (`/api/locations`)
- **`models/`**: SQLite table creation (items, users)
- **`services/kroger_api.py`**: Kroger API integration for products, pricing, and locations

### Frontend Structure (`grocery_frontend/src/`)
- **`App.jsx`**: Main component with routing (/, /login, /signup)
- **`context/AuthContext.js`**: React context for authentication state
- **`pages/`**: Page components (homePage, loginPage, signupPage)
- **`modal.jsx`**: Reusable modal component for store selection

### Key Data Flow
1. User authentication passes `userId` header with all API requests
2. Items track purchase history (`total_purchases`, `previous_purchased_prices`) for suggestions
3. Suggestions route compares current Kroger prices against historical averages to detect sales
4. Store selection sends `zipCode` header to locations endpoint

### API Authentication Pattern
- User ID is passed via `userId` HTTP header (not URL params or body)
- Kroger API uses OAuth2 client credentials flow (`kroger_api.getToken()`)

## Configuration Requirements

Create `grocery_backend/config.py` with:
- `DB_PATH`: Path to SQLite database
- `KROGER_CLIENT_ID`, `KROGER_CLIENT_SECRET`: Kroger API credentials
- `KROGER_TOKEN_URL`, `KROGER_API_BASE_URL`: Kroger API endpoints
- `STORE_ID`: Default Kroger location ID for pricing
- `API_PREFIX`: API route prefix (e.g., "/api")
- `ALLOWED_ORIGINS`, `DEBUG`, `PORT`: Flask settings
