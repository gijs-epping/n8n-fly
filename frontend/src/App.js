import React from 'react';
import './App.css';
import FormulaBuilder from './components/FormulaBuilder';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Formula Builder App</h1>
      </header>
      <main className="App-main">
        <FormulaBuilder />
      </main>
    </div>
  );
}

export default App;
