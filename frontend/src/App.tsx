import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './layouts/Navbar';
import { Footer } from './layouts/Footer';
import { Landing } from './pages/Landing';
import { Dashboard } from './pages/Dashboard';
import { Analytics } from './pages/Analytics';
import { Simulations } from './pages/Simulations';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';
import { NotFound } from './pages/NotFound';

const App: React.FC = () => {
  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-cyber-black text-gray-100 selection:bg-cyber-cyan/30 selection:text-white">
        {/* Navbar */}
        <Navbar />

        {/* Main Content Area */}
        <main className="flex-1 w-full">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route
              path="/dashboard"
              element={
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <Dashboard />
                </div>
              }
            />
            <Route
              path="/analytics"
              element={
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <Analytics />
                </div>
              }
            />
            <Route
              path="/simulations"
              element={
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <Simulations />
                </div>
              }
            />
            <Route
              path="/reports"
              element={
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <Reports />
                </div>
              }
            />
            <Route
              path="/settings"
              element={
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <Settings />
                </div>
              }
            />
            <Route
              path="*"
              element={
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                  <NotFound />
                </div>
              }
            />
          </Routes>
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </Router>
  );
}

export default App;
