import React, { useEffect, useState } from 'react';
import ShopBanner from './ShopBanner';

const API_URL = import.meta.env.VITE_API_URL || '';

const Shop = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');
    const [checkoutLoading, setCheckoutLoading] = useState(null);

    useEffect(() => {
        // Check for success or cancel from URL
        const query = new URLSearchParams(window.location.search);
        if (query.get('success')) {
            setMessage('Order placed! You will receive an email confirmation.');
        }
        if (query.get('canceled')) {
            setMessage('Order canceled -- continue to shop around and checkout when you\'re ready.');
        }

        fetch(`${API_URL}/shop/products`)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                return res.json();
            })
            .then(data => {
                setProducts(data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching products", err);
                setError(`Failed to load products: ${err.message}`);
                setLoading(false);
            });
    }, []);

    const handleBuy = async (priceId) => {
        if (!priceId || priceId.includes('example') || priceId.includes('...')) {
            setError('This product does not have a valid Stripe Price ID configured.');
            return;
        }

        setCheckoutLoading(priceId);
        try {
            const response = await fetch(`${API_URL}/shop/create-checkout-session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ price_id: priceId }),
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to create checkout session');
            }
            
            const session = await response.json();
            if (session.url) {
                window.location.href = session.url;
            } else {
                setError('No checkout URL received');
            }
        } catch (err) {
            console.error("Error redirecting to Stripe", err);
            setError(`Checkout error: ${err.message}`);
            setCheckoutLoading(null);
        }
    };

    if (loading) return <p>Loading shop...</p>;

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <ShopBanner />
            <h2>E-Shop</h2>
            {error && (
                <div style={{ 
                    backgroundColor: '#f8d7da', 
                    color: '#721c24', 
                    padding: '10px', 
                    borderRadius: '4px', 
                    marginBottom: '15px',
                    border: '1px solid #f5c6cb'
                }}>
                    {error}
                </div>
            )}
            {message && (
                <div style={{ 
                    backgroundColor: '#d4edda', 
                    color: '#155724', 
                    padding: '10px', 
                    borderRadius: '4px', 
                    marginBottom: '15px',
                    border: '1px solid #c3e6cb'
                }}>
                    {message}
                </div>
            )}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '20px' }}>
                {products.length > 0 ? (
                    products.map((product) => (
                        <div key={product.id} style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '8px', textAlign: 'center' }}>
                            {product.image_url && (
                                <img 
                                    src={product.image_url} 
                                    alt={product.name} 
                                    style={{ maxWidth: '100%', height: 'auto', marginBottom: '10px', maxHeight: '200px', objectFit: 'contain' }} 
                                />
                            )}
                            <h3>{product.name}</h3>
                            <p>{product.description}</p>
                            <p style={{ fontWeight: 'bold', fontSize: '18px' }}>${parseFloat(product.price).toFixed(2)}</p>
                            <button 
                                onClick={() => handleBuy(product.stripe_price_id)}
                                disabled={checkoutLoading === product.stripe_price_id}
                                style={{ 
                                    backgroundColor: checkoutLoading === product.stripe_price_id ? '#999' : '#6772e5', 
                                    color: 'white', 
                                    padding: '10px 15px', 
                                    border: 'none', 
                                    borderRadius: '4px', 
                                    cursor: checkoutLoading === product.stripe_price_id ? 'not-allowed' : 'pointer',
                                    opacity: checkoutLoading === product.stripe_price_id ? 0.6 : 1
                                }}
                            >
                                {checkoutLoading === product.stripe_price_id ? 'Processing...' : 'Buy Now'}
                            </button>
                        </div>
                    ))
                ) : (
                    <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '40px' }}>
                        <p style={{ fontSize: '18px', color: '#666' }}>
                            No products available yet. Try seeding the database at <code>/shop/seed-products</code>!
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Shop;
