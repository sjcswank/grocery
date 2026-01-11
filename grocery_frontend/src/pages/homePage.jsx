import React, { useState, useEffect } from 'react';
import { Plus, X, Check, Search } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Modal from '../modal';
import '../modal.css'

const API_URL = 'http://localhost:5000/api';


function HomePage() {
    const { user, isAuthenticated, setError } = useAuth();
    const [currentList, setCurrentList] = useState([]);
    const [previousList, setPreviousList] = useState([]);
    const [suggestionsList, setSuggestionsList] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [loading, setLoading] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [zipcode, setZipcode] = useState('');
    const [locations, setLocations] = useState([]);
    const [currentStore, setCurrentStore] = useState({});
    setError(null);

    // Fetch data on component mount
    useEffect(() => {
        //TODO: Refactor so Loading displays while fetching data on first load
        try {
            fetchData('items');
            fetchData('previous');
            fetchData('suggestions');
        }
        catch (err) {}
    }, []);


    const fetchData = async (endPoint) => {
        setLoading(true);
        try {           
            const response = await fetch(`${API_URL}/${endPoint}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'userId': user.id
                },
            })

            if (!response.ok) {
                throw new Error('Failed to fetch data');
            }
            const items = await response.json();
            if (endPoint === 'items') { setCurrentList(items); }
            if (endPoint === 'previous') { setPreviousList(items); }
            if (endPoint === 'suggestions') { setSuggestionsList(items); }
            else { throw new Error('Incorrect endpoint')}

            setError(null);

        }
        catch (err) {
            console.log(err.message);
            setError(err.message);
        }
        finally {
            setInputValue('');
            setLoading(false);
        }
    }

    const addItem = async (itemName) => {
        setLoading(true);
        if (!itemName.trim() || currentList.find(item => item.name.toLowerCase() === itemName.toLowerCase())) {
        }
        else {
            try {
                const response = await fetch(`${API_URL}/items`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'userId': user.id, },
                    body: JSON.stringify({ name: itemName.trim() })
                });
                
                if (!response.ok) throw new Error('Failed to add item');
                //DONE: Add item to current list
                const item = await response.json();
                setCurrentList(currentItems => [...currentItems, item]);
            } catch (err) {
                setError('Failed to add item');
            }
        }
        setInputValue('');
        setLoading(false);
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
    }
  };

  const removeItem = async (id) => {
    setLoading(true);
    const item = currentList.find(i => i.id === id);
    
    // Optimistic update
    setCurrentList(currentList.filter(item => item.id !== id));

    try {
      const response = await fetch(`${API_URL}/items/${id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({price: item.price})
      });
      
      if (!response.ok) throw new Error('Failed to delete item');
      fetchData('previous');
    } catch (err) {
        // Revert on error
        setCurrentList([...currentList, item]);
        setError('Failed to delete item');
    }
    setLoading(false);
  };

  const getStores = async (zipcode) => {
    setLocations([]);
    try {
        const response = await fetch(`${API_URL}/locations`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json', 'zipCode': zipcode }
        });
        if(!response.ok) throw new Error('Failed to fetch locations');
        const list = await response.json();
        setLocations(list);
    } 
    catch (err) { }
    finally { setZipcode(''); }
  }

  const closeModal = () => {
    setCurrentStore({});
    setIsModalOpen(false);
  }

  const confirmLocation = () => {
    setLocations([]);
    setZipcode('');
    setIsModalOpen(false);
  }

  if (!isAuthenticated) {
    setError('You must be logged in to see this page.')
    return (
        <div>
        </div>
    )
  }
  else {
    return (
        <div>
            {loading ? (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg mb-6">
              Loading...
            </div>
            ) : (
            <div>    
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

            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
                <div className="flex gap-2">
                {Object.keys(currentStore).length === 0 ? (<p className='flex-1'>Please Select a Store</p>) : (
                    <h2 className="flex-1 text-lg font-medium text-neutral-700 mb-4">{currentStore.name}<br />
                    <span className='text-sm'>{currentStore.address.addressLine1}, {currentStore.address.city}, {currentStore.address.state}</span></h2>
                )}
            <button className='h-10 px-4 py-2 bg-neutral-800 text-white rounded-md hover:bg-neutral-700 transition-colors' onClick={() => setIsModalOpen(true)}>
                Select Store
            </button>
            <Modal 
                isOpen={isModalOpen} 
                onClose={() => closeModal()} 
                title="Select Store"
                closeText="Select Store"
                onConfirm={() => confirmLocation()}>
                <p>Search by Zipcode.</p>
                <div className="flex py-2 m-2">
                    <input
                        type="text"
                        value={zipcode}
                        onChange={(e) => setZipcode(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && getStores(zipcode)}
                        placeholder="Enter zipcode..."
                        className="flex-1 px-4 py-2 border border-neutral-200 rounded-md focus:outline-none focus:ring-2 focus:ring-neutral-400"
                    />
                    <button
                        onClick={() => getStores(zipcode)}
                        className="px-4 py-2 bg-neutral-800 text-white rounded-md hover:bg-neutral-700 transition-colors"
                    >
                        <Search size={20} />
                    </button>
                </div>
                <div className='py-3'>
                    {locations.length === 0 ? (
                        <p className="text-neutral-400 text-center py-8">No locations. Please enter a zipcode.</p>
                    ) : (
                        <div class="space-y-4">
                        {locations.map(location => {
                            return (
  
                                <div 
                                    class="cursor-pointer bg-neutral-100 hover:bg-neutral-200 p-4 rounded shadow transition duration-150 ease-in-out"
                                    onClick={() => setCurrentStore(location)}
                                >
                                    
                                    <div class="flex items-center gap-4 mb-4">
                                    
                                        <div class="grow text-left">
                                            {location.name}
                                        </div>

                                        <div class="w-40 flex items-center justify-center text-sm font-medium text-neutral-700 shrink-0">
                                            {location.phone}
                                        </div>
                                    </div>

                                    <div class="w-full text-left text-sm text-neutral-700">
                                        {location.address.addressLine1}, {location.address.city}, {location.address.state}
                                    </div>
                                    
                                </div>

                            )
                        })}
                        </div>
                    )}
                </div>
            </Modal>
            </div>
                <h2 className="text-lg font-medium text-neutral-700 mb-4">Current List</h2>
                {currentList.length === 0 ? (
                <p className="text-neutral-400 text-center py-8">No items yet. Add some items to get started!</p>
                ) : (
                <div className="space-y-2">
                    {currentList.map(item => {
                        return (
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
                        <span className="flex-1 text-neutral-800">
                        {/* Price: {Math.min(...prices)} */}
                        Price: {item.price}
                        </span>
                        <button
                        onClick={() => removeItem(item.id)}
                        className="text-neutral-400 hover:text-neutral-600 transition-colors"
                        >
                        <X size={18} />
                        </button>
                    </div>
                        );
                    })}
                </div>)}
            </div>

            {suggestionsList.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
                <h2 className="text-lg font-medium text-neutral-700 mb-4">Suggested Items</h2>
                <div className="flex flex-wrap gap-2">
                {suggestionsList.map(item => (
                    <button 
                    key={item.name}
                    onClick={() => addItem(item.name)}
                    disabled={currentList.some(i => i.name.toLowerCase() === item.name.toLowerCase())}
                    className={`px-3 py-1.5 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${item.sale ? 'bg-green-100 text-green-700 text-sm hover:bg-green-200' : 'bg-neutral-100 text-neutral-700 text-sm hover:bg-neutral-200'}`}
                    >
                    {item.name}
                    </button>
                ))}
                </div>
            </div>)}

            {previousList.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm p-4">
                    <h2 className="text-lg font-medium text-neutral-700 mb-4">Previously Bought</h2>
                    <div className="flex flex-wrap gap-2">
                        {previousList.map(item => (
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
    )}
    </div>
    )}     
}
export default HomePage;