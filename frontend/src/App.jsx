import React, { useEffect, useState } from 'react'
import Portfolio from './components/Portfolio'
import Blog from './components/Blog'
import Shop from './components/Shop'

const API_URL = import.meta.env.VITE_API_URL || '';

/**
 * Error Boundary component to catch and display errors
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', margin: '20px' }}>
          <h3>Something went wrong</h3>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  /**
   * @typedef {Object} ApiData
   * @property {string} message
   * @property {string} [r2_public_domain]
   * @property {string} [r2_bucket_name]
   */

  /** @type {[ApiData|null, React.Dispatch<React.SetStateAction<ApiData|null>>]} */
  const [data, setData] = useState(null)
  const [view, setView] = useState('home')
  const [apiError, setApiError] = useState('')
  const [apiLoading, setApiLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_URL}/`)
      .then(res => {
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
      })
      .then(setData)
      .catch(err => {
        console.error("Error connecting to API", err);
        setApiError(`Failed to connect to API: ${err.message}`);
      })
      .finally(() => setApiLoading(false))
  }, [])

  return (
    <ErrorBoundary>
      <nav style={{ 
        padding: '10px 60px',
        backgroundColor: '#333', 
        color: 'white', 
        display: 'fixed',
        gap: '10px',
        position: 'fixed',
        top: 0,
        left: '50%',
        transform: 'translateX(-50%)',
        width: '1126px',
        maxWidth: '100%',
        zIndex: 1000,
        boxSizing: 'border-box',
        borderInline: '1px solid var(--border)'
      }}>
        <button 
          onClick={() => setView('home')} 
          style={{ 
            padding: '5px 10px', 
            cursor: 'pointer',
            backgroundColor: view === 'home' ? '#555' : 'transparent',
            border: 'none',
            color: 'white',
            borderRadius: '4px'
          }}
        >
          Home / Shop
        </button>
        <button 
          onClick={() => setView('portfolio')} 
          style={{ 
            padding: '5px 10px', 
            cursor: 'pointer',
            backgroundColor: view === 'portfolio' ? '#555' : 'transparent',
            border: 'none',
            color: 'white',
            borderRadius: '4px'
          }}
        >
          Portfolio
        </button>
        <button 
          onClick={() => setView('blog')} 
          style={{ 
            padding: '5px 10px', 
            cursor: 'pointer',
            backgroundColor: view === 'blog' ? '#555' : 'transparent',
            border: 'none',
            color: 'white',
            borderRadius: '4px'
          }}
        >
          Blog
        </button>
      </nav>
      
      <div style={{ paddingTop: '80px' }}>
        {apiError && (
          <div style={{ padding: '15px', margin: '10px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px' }}>
            <strong>API Connection Error:</strong> {apiError}
          </div>
        )}
        
        {apiLoading && (
          <div style={{ padding: '15px', margin: '10px', backgroundColor: '#e2e3e5', color: '#383d41', borderRadius: '4px' }}>
            Loading...
          </div>
        )}

        <div style={{ padding: '20px' }}>
          {view === 'home' ? (
            <Shop />
          ) : view === 'portfolio' ? (
            <Portfolio />
          ) : (
            <Blog />
          )}
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default App
