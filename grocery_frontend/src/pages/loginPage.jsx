import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const API_URL = 'http://localhost:5000/api';

function LoginPage() {
  const navigate = useNavigate();
  const { login, setError } = useAuth();
  const [usernameValue, setUserName] = useState('');
  const [passwordValue, setUserPasword] = useState('');
  setError(null);


  const loginUser = async (username, password) => {

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({username: username, password: password})
        });

        if (!response.ok) throw new Error('Failed to login.');

        const user = await response.json();

        login(user);
        setUserName('');
        setUserPasword('');

        navigate('/');
    } catch (err) {
        console.log(err.Error);
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
      <div className="flex gap-2">
        <input
          type="text"
          value={usernameValue}
          onChange={(e) => setUserName(e.target.value)}
          placeholder="Username"
          className="flex-1 px-4 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-neutral-400"
        />
        <input
          type="text"
          value={passwordValue}
          onChange={(e) => setUserPasword(e.target.value)}
          placeholder="Password"
          className="flex-1 px-4 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-neutral-400"
        />

        <button
          onClick={() => loginUser(usernameValue, passwordValue)}
          className="px-4 py-2 bg-neutral-800 text-white rounded-md hover:bg-neutral-700 transition-colors"
        >
          Login
        </button>
      </div>
    </div>
    );
  }
export default LoginPage;


        