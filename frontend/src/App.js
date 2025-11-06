import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ConversationList from './components/ConversationList';
import ConversationDetail from './components/ConversationDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <Link to="/" className="App-title">
            <h1>💬 Realmate Challenge</h1>
          </Link>
        </header>
        <main className="App-main">
          <Routes>
            <Route path="/" element={<ConversationList />} />
            <Route path="/conversation/:id" element={<ConversationDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

