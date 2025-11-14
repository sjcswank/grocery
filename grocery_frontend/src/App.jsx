import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import SignupPage from './pages/signupPage';
import HomePage from './pages/homePage';
import LoginPage from './pages/loginPage';
import { useAuth } from './context/AuthContext';
import { useNavigate } from 'react-router-dom';



export default function GroceryListApp() {
  const { isAuthenticated, error, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const logoutUser = () => {
    logout();
    navigate('/login');
  }


  return (
      <div className="min-h-screen bg-neutral-50 p-4 sm:p-8">
      <div className="flex max-w-2xl mx-auto p-4 mb-6">
        <div className="w-1/2">
          <h1 className="text-3xl font-light text-neutral-800">Grocery List</h1>
        </div>
        <div className="flex w-1/2 justify-end">
          {isAuthenticated ? (
            <button
              onClick={() => logoutUser()}
              className="px-4 py-2 bg-neutral-800 text-white rounded-md hover:bg-neutral-700 transition-colors"
            >Logout
            </button>
          ) : location.pathname === "/login" ? (
            <button
              onClick={() => navigate('/signup')}
              className="px-4 py-2 bg-neutral-800 text-white rounded-md hover:bg-neutral-700 transition-colors"
            >Signup
            </button>
          ) : 
          (<button
              onClick={() => navigate('/login')}
              className="px-4 py-2 bg-neutral-800 text-white rounded-md hover:bg-neutral-700 transition-colors"
            >Login
          </button>)}
        </div>
      </div>
      <div className="max-w-2xl mx-auto">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <Routes>
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
          </Routes>
          
        </div>
      </div>
  );
}