import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import FloatingChatWidget from './components/FloatingChatWidget';
import Dashboard from './pages/Dashboard';
import AuditNew from './pages/AuditNew';
import Auth from './pages/Auth';
import Library from './pages/Library';
import Settings from './pages/Settings';
import Landing from './pages/Landing';
import Compare from './pages/Compare';
import Compliance from './pages/Compliance';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/auth" element={<Auth />} />

            {/* Protected Routes sharing a persistent Layout */}
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/audit" element={<AuditNew />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/compliance" element={<Compliance />} />
              <Route path="/library" element={<Library />} />
              <Route path="/settings" element={<Settings />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

const ProtectedRoute = () => {
  const { user } = useAuth();
  if (!user) return <Navigate to="/" replace />;

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900 overflow-hidden text-slate-900 dark:text-slate-50 font-sans antialiased transition-colors duration-200 relative">
      <Sidebar />
      <main className="flex-1 ml-64 flex flex-col h-full overflow-hidden">
        <Header />
        <div className="flex-1 overflow-y-auto w-full">
          <Outlet />
        </div>
      </main>

      {/* Persistent RAG Chatbot Floating Launcher & Widget */}
      <FloatingChatWidget />
    </div>
  );
};

export default App;
