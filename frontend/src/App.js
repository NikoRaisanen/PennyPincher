import React, { useEffect, useState } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import logo from './logo.svg';
import './App.css';

function App() {
  const [linkToken, setLinkToken] = useState(null);
  useEffect(() => {
    fetch('http://localhost:8000/api/create_link_token')
      .then((response) => response.json())
      .then((data) => setLinkToken(data.link_token))
      .catch((error) => console.error('Error:', error));
  }, []);  // run once on-mount

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess: (public_token, metadata) => {
      console.log('Success:', public_token, metadata);
      fetch('http://localhost:8000/api/exchange_public_token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ public_token }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log('Access Token:', data.access_token);
          console.log('Item ID:', data.item_id);
          // TODO: do something with the access token
        })
        .catch((error) => console.error('Error:', error));
    },
    onExit: (err, metadata) => {
      console.log('Exit:', err, metadata);
    },
    onEvent: (eventName, metadata) => {
      console.log('Event:', eventName, metadata);
    },
  });

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>Edit <code>src/App.js</code> and save to reload.</p>
        <button onClick={() => open()} disabled={!ready}>
          Connect to Plaid
        </button>
      </header>
    </div>
  );
}

export default App;
