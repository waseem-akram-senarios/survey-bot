import React from 'react';

const SurveyBuilderMinimal = () => {
  return React.createElement('div', {
    style: {
      padding: '40px',
      textAlign: 'center',
      backgroundColor: '#f0f0f0',
      minHeight: '100vh'
    }
  }, [
    React.createElement('h1', { key: 'title' }, 'Survey Builder Minimal Test'),
    React.createElement('p', { key: 'desc' }, 'If you see this, React is working!'),
    React.createElement('button', { 
      key: 'btn',
      onClick: () => alert('Button clicked!')
    }, 'Click Me')
  ]);
};

export default SurveyBuilderMinimal;
