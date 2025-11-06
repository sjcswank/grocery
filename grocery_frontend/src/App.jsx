import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import SignupPage from './pages/signupPage';
import { Plus, X, Check } from 'lucide-react';
import { useAuth } from './context/AuthContext';

const API_URL = 'http://localhost:5000/api';

export default function GroceryListApp() {
  const { user, isAuthenticated } = useAuth();
  const [currentList, setCurrentList] = useState([]);
  const [previousItems, setPreviousItems] = useState([]);
  const [suggestedItems, setSuggestedItems] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // "State":
  //   "currentList": [
  //      {"id": 10, "name": "Apples", "bought": False},
  //      {"id": 11, "name": "Oranges", "bought": True}.
  //      {"id": 12. "name": "Grapes", "bought": False}
  //    ],
  //   "previousItems": [
  //      {"id": 09, "name": "Milk", "bought_date": 2025-11-4-8:56:00},
  //      {"id": 08, "name": "Eggs", "bought_date": 2025-11-4-8:55:00},
  //      {"id": 07, "name": "Bread", "bought_date": 2025-11-4-8:54:00}
  //    ],
  //   "inputValue": '',
  //   "loading": true,
  //   "error": null

  // Fetch data on component mount
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    if (isAuthenticated)
      try {
        setLoading(true);
        const [itemsRes, previousRes, suggestedRes] = await Promise.all([
          fetch(`${API_URL}/items`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              userId: user.id
            }),
          }),
          fetch(`${API_URL}/previous`),
          fetch(`${API_URL}/suggestions`)
        ]);
        
        if (!itemsRes.ok || !previousRes.ok || !suggestedRes) {
          throw new Error('Failed to fetch data');
        }
        
        const items = await itemsRes.json();
        const previous = await previousRes.json();
        const suggested = await suggestedRes.json();
        setCurrentList(items);
        setPreviousItems(previous);
        setSuggestedItems(suggested);
        setError(null);
      } catch (err) {
        setError('Failed to load data. Make sure the backend server is running.');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    else 
      setError('You must be logged in to see this page.');
      setLoading(false);
  };

  const addItem = async (itemName) => {
    if (!itemName.trim() || currentList.find(item => item.name.toLowerCase() === itemName.toLowerCase())) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: itemName.trim(), user_id: user.id })
      });
      
      if (!response.ok) throw new Error('Failed to add item');
      
      const newItem = await response.json();
      setCurrentList([...currentList, newItem]);
      setInputValue('');
      // Refresh Data
      const previousRes = await fetch(`${API_URL}/previous`);
      const previous = await previousRes.json();
      setPreviousItems(previous);
      const suggestedRes = await fetch(`${API_URL}/suggestions`);
      const suggested = await suggestedRes.json();
      setSuggestedItems(suggested);
    } catch (err) {
      setError('Failed to add item');
      console.error('Error adding item:', err);
    }
  };

  const toggleBought = async (id) => {
    const item = currentList.find(i => i.id === id);
    const newBoughtStatus = !item.bought;

    // Optimistic update
    setCurrentList(currentList.map(item => 
      item.id === id ? { ...item, bought: newBoughtStatus } : item
    ));

    try {
      const response = await fetch(`${API_URL}/items/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bought: newBoughtStatus })
      });
      
      if (!response.ok) throw new Error('Failed to update item');
    } catch (err) {
      // Revert on error
      setCurrentList(currentList.map(item => 
        item.id === id ? { ...item, bought: !newBoughtStatus } : item
      ));
      setError('Failed to update item');
      console.error('Error updating item:', err);
    }
  };

  const removeItem = async (id) => {
    const item = currentList.find(i => i.id === id);
    
    // Optimistic update
    setCurrentList(currentList.filter(item => item.id !== id));

    try {
      const response = await fetch(`${API_URL}/items/${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Failed to delete item');
      
      // Refresh Data
      const previousRes = await fetch(`${API_URL}/previous`);
      const previous = await previousRes.json();
      setPreviousItems(previous);
      const suggestedRes = await fetch(`${API_URL}/suggestions`);
      const suggested = await suggestedRes.json();
      setSuggestedItems(suggested);
    } catch (err) {
      // Revert on error
      setCurrentList([...currentList, item]);
      setError('Failed to delete item');
      console.error('Error deleting item:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-neutral-600">Loading...</div>
      </div>
    );
  }

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

          <Routes>
            <Route path="/signup" element={<SignupPage />} />
          </Routes>
          
          {/* Add Item Input */}
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addItem(inputValue)}
                placeholder="Add an item..."
                className="flex-1 px-4 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-neutral-400"
              />
              <button
                onClick={() => addItem(inputValue)}
                className="px-4 py-2 bg-neutral-800 text-white rounded-md hover:bg-neutral-700 transition-colors"
              >
                <Plus size={20} />
              </button>
            </div>
          </div>

          {/* Current List */}
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
            <h2 className="text-lg font-medium text-neutral-700 mb-4">Current List</h2>
            {currentList.length === 0 ? (
              <p className="text-neutral-400 text-center py-8">No items yet. Add some items to get started!</p>
            ) : (
              <div className="space-y-2">
                {currentList.map(item => (
                  <div
                    key={item.id}
                    className="flex items-center gap-3 p-3 rounded-md hover:bg-neutral-50 transition-colors"
                  >
                    <button
                      onClick={() => toggleBought(item.id)}
                      className={`w-6 h-6 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                        item.bought
                          ? 'bg-neutral-800 border-neutral-800'
                          : 'border-neutral-300 hover:border-neutral-400'
                      }`}
                    >
                      {item.bought && <Check size={16} className="text-white stroke-2" />}
                    </button>
                    <span className={`flex-1 ${item.bought ? 'line-through text-neutral-400' : 'text-neutral-800'}`}>
                      {item.name}
                    </span>
                    <button
                      onClick={() => removeItem(item.id)}
                      className="text-neutral-400 hover:text-neutral-600 transition-colors"
                    >
                      <X size={18} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Suggested Items */}
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
            <h2 className="text-lg font-medium text-neutral-700 mb-4">Suggested Items</h2>
            <div className="flex flex-wrap gap-2">
              {suggestedItems.map(item => (
                <button
                  key={item}
                  onClick={() => addItem(item)}
                  disabled={currentList.some(i => i.name.toLowerCase() === item.toLowerCase())}
                  className="px-3 py-1.5 bg-neutral-100 text-neutral-700 rounded-full text-sm hover:bg-neutral-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          {/* Previously Bought Items */}
          {previousItems.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h2 className="text-lg font-medium text-neutral-700 mb-4">Previously Bought</h2>
              <div className="flex flex-wrap gap-2">
                {previousItems.map(item => (
                  <button
                    key={item}
                    onClick={() => addItem(item)}
                    disabled={currentList.some(i => i.name.toLowerCase() === item.toLowerCase())}
                    className="px-3 py-1.5 bg-neutral-50 text-neutral-600 rounded-full text-sm border border-neutral-200 hover:bg-neutral-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Router>
  );
}