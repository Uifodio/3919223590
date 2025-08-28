import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [platform, setPlatform] = useState('');
  const [appVersion, setAppVersion] = useState('');

  useEffect(() => {
    // Get platform info from Electron
    if (window.electronAPI) {
      setPlatform(window.electronAPI.getPlatform());
      
      // Get app version
      window.electronAPI.getAppVersion().then(version => {
        setAppVersion(version);
      }).catch(err => {
        console.log('Could not get app version:', err);
      });
    }
  }, []);

  const handleSendMessage = () => {
    if (window.electronAPI && message.trim()) {
      window.electronAPI.sendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="logo-container">
          <div className="electron-logo">⚛️</div>
          <h1>React + Electron</h1>
        </div>
        <p className="subtitle">Sample Application</p>
      </header>

      <main className="App-main">
        <div className="info-cards">
          <div className="info-card">
            <h3>Platform</h3>
            <p>{platform || 'Loading...'}</p>
          </div>
          
          <div className="info-card">
            <h3>App Version</h3>
            <p>{appVersion || 'Loading...'}</p>
          </div>
          
          <div className="info-card">
            <h3>Environment</h3>
            <p>{process.env.NODE_ENV || 'development'}</p>
          </div>
        </div>

        <div className="message-section">
          <h3>Send Message to Main Process</h3>
          <div className="message-input">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type a message..."
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <button onClick={handleSendMessage} disabled={!message.trim()}>
              Send
            </button>
          </div>
        </div>

        <div className="features">
          <h3>Features</h3>
          <ul>
            <li>✅ React 18 with modern hooks</li>
            <li>✅ Electron main process</li>
            <li>✅ Secure preload script</li>
            <li>✅ Hot reload in development</li>
            <li>✅ Production build support</li>
            <li>✅ Cross-platform compatibility</li>
          </ul>
        </div>
      </main>

      <footer className="App-footer">
        <p>Built with React + Electron</p>
      </footer>
    </div>
  );
}

export default App;