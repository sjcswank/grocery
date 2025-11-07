import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SignupPage from './pages/signupPage';
import HomePage from './pages/homePage';
import LoginPage from './pages/loginPage';
import { useAuth } from './context/AuthContext';


export default function GroceryListApp() {
  const { isAuthenticated, error, logout } = useAuth();


  return (
    <Router>
      <div className="min-h-screen bg-neutral-50 p-4 sm:p-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-light text-neutral-800 mb-8">Grocery List</h1>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {isAuthenticated && (
            <button onClick={() => logout()}>
              Logout
            </button>
          )}
          
          <Routes>
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
          </Routes>
          
        </div>
      </div>
    </Router>
  );
}