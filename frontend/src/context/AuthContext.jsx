/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [isLoading, setIsLoading] = useState(false);

  /** Listen for 401 events dispatched by api.js and auto-logout. */
  useEffect(() => {
    const handleForcedLogout = () => {
      setUser(null);
    };
    window.addEventListener('auth:logout', handleForcedLogout);
    return () => window.removeEventListener('auth:logout', handleForcedLogout);
  }, []);

  const _handleAuthResponse = (data) => {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
  };

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const data = await api.post('/api/auth/login', { email, password });
      _handleAuthResponse(data);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (name, email, password, role) => {
    setIsLoading(true);
    try {
      const data = await api.post('/api/auth/signup', { name, email, password, role });
      _handleAuthResponse(data);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * googleLogin — sends the Google ID token credential to the backend.
   * The backend verifies it, resolves/creates the user, and returns the
   * same Token structure as email/password login.
   * The rest of the app does not need to know the auth method.
   */
  const googleLogin = async (credential) => {
    setIsLoading(true);
    try {
      const data = await api.post('/api/auth/google', { credential });
      _handleAuthResponse(data);
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = async (name, role) => {
    setIsLoading(true);
    try {
      const updatedUser = await api.put('/api/auth/profile', { name, role });
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);
      return updatedUser;
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updatePassword = async (current_password, new_password) => {
    setIsLoading(true);
    try {
      const res = await api.put('/api/auth/password', { current_password, new_password });
      return res;
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, googleLogin, updateProfile, updatePassword, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
