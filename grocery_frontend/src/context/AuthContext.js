import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);


export const AuthProvider = ({ children }) => {
  // Define your global state here
  const [user, setUser ] = useState(null);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Define functions to update the state
  const login = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setError(null);
  };

  // The value prop contains everything you want to share globally
  const value = {
    user,
    error,
    isAuthenticated,
    login,
    logout,
    setError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};