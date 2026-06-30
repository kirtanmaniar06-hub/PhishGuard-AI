import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { Navbar } from './layouts/Navbar';
import { Footer } from './layouts/Footer';
import { Landing } from './pages/Landing';
import { Dashboard } from './pages/Dashboard';
import { Analytics } from './pages/Analytics';
import { Simulations } from './pages/Simulations';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';
import { NotFound } from './pages/NotFound';
import { DashboardLayout } from './layouts/DashboardLayout';

import { EmailScanner } from './components/EmailScanner';

const AppContent: React.FC = () => {
  const location = useLocation();
  const dashboardRoutes = ['/dashboard', '/analytics', '/simulations', '/reports', '/settings', '/email-scanner'];
  const isDashboardRoute = dashboardRoutes.some(path => location.pathname.startsWith(path));

  if (isDashboardRoute) {
    return (
      <DashboardLayout>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/email-scanner" element={<EmailScanner />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/simulations" element={<Simulations />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </DashboardLayout>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-cyber-black text-gray-100 selection:bg-cyber-cyan/30 selection:text-white">
      {/* Navbar */}
      <Navbar />

      {/* Main Content Area */}
      <main className="flex-1 w-full">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;

