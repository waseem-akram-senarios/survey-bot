import React from 'react';

const TestPage = () => {
  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f0f0f0',
      minHeight: '100vh'
    }}>
      <h1 style={{ color: '#333', textAlign: 'center' }}>
        🎉 React is Working!
      </h1>
      <p style={{ textAlign: 'center', color: '#666' }}>
        If you can see this, React is rendering correctly.
      </p>
      <div style={{ 
        textAlign: 'center', 
        marginTop: '20px',
        padding: '10px',
        backgroundColor: '#fff',
        borderRadius: '5px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <p>Current URL: {window.location.href}</p>
        <p>Timestamp: {new Date().toLocaleString()}</p>
      </div>
    </div>
  );
};

export default TestPage;
