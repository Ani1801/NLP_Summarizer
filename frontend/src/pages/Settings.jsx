import React, { useState, useEffect } from 'react';
import { User, Lock, Bell, Moon, Shield, Smartphone, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const Settings = () => {
  const { user, updateProfile, updatePassword, isLoading } = useAuth();
  const { theme, switchTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('profile');

  // Profile form state
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    role: user?.role || 'Researcher',
  });

  // Password form state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Feedback notifications
  const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });

  useEffect(() => {
    if (user) {
      setProfileData({
        name: user.name || '',
        role: user.role || 'Researcher',
      });
    }
  }, [user]);

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setStatusMsg({ type: '', text: '' });
    try {
      await updateProfile(profileData.name, profileData.role);
      setStatusMsg({ type: 'success', text: 'Profile updated successfully!' });
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to update profile.' });
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setStatusMsg({ type: '', text: '' });

    if (passwordData.new_password.length < 6) {
      setStatusMsg({ type: 'error', text: 'New password must be at least 6 characters long.' });
      return;
    }
    if (passwordData.new_password !== passwordData.confirm_password) {
      setStatusMsg({ type: 'error', text: 'New passwords do not match.' });
      return;
    }

    try {
      const res = await updatePassword(passwordData.current_password, passwordData.new_password);
      setStatusMsg({ type: 'success', text: res.message || 'Password updated successfully!' });
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to update password.' });
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'security':
        return (
          <>
            <div className="px-8 py-6 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3">
              <div className="p-2 bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-400 rounded-lg">
                <Lock size={20} />
              </div>
              <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">Security Parameters</h2>
            </div>

            <div className="p-8 space-y-8">
              {statusMsg.text && (
                <div
                  className={`p-4 rounded-xl flex items-center gap-3 text-sm font-semibold border ${
                    statusMsg.type === 'success'
                      ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300'
                      : 'bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300'
                  }`}
                >
                  {statusMsg.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
                  <span>{statusMsg.text}</span>
                </div>
              )}

              <form onSubmit={handlePasswordSubmit} className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Change Password</h3>

                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Current Password</label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                    required
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:text-white transition-all"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-slate-100 dark:border-slate-800 pt-4 mt-4">
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">New Password</label>
                    <input
                      type="password"
                      placeholder="••••••••"
                      value={passwordData.new_password}
                      onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                      required
                      className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:text-white transition-all"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Confirm Password</label>
                    <input
                      type="password"
                      placeholder="••••••••"
                      value={passwordData.confirm_password}
                      onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                      required
                      className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:text-white transition-all"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="bg-blue-600 text-white px-5 py-2.5 rounded-lg font-semibold hover:bg-blue-700 transition duration-200 shadow-sm mt-2 flex items-center gap-2 disabled:opacity-50 cursor-pointer"
                >
                  {isLoading && <Loader2 size={16} className="animate-spin" />}
                  Update Password
                </button>
              </form>

              <div className="border-t border-slate-100 dark:border-slate-800 pt-8 space-y-4">
                <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
                  <Shield size={18} className="text-emerald-500" /> Two-Factor Authentication (2FA)
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">Adds an extra layer of security to your account natively.</p>
                <div className="flex items-center justify-between p-4 border border-slate-200 dark:border-slate-700 rounded-xl bg-slate-50 dark:bg-slate-800">
                  <div className="flex items-center gap-3">
                    <Smartphone size={20} className="text-slate-400" />
                    <div>
                      <p className="font-semibold text-slate-800 dark:text-slate-200">Authenticator App</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">Not configured</p>
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200 font-medium rounded-lg hover:bg-slate-50 dark:hover:bg-slate-600 transition-colors">
                    Setup
                  </button>
                </div>
              </div>
            </div>
          </>
        );

      case 'notifications':
        return (
          <>
            <div className="px-8 py-6 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3">
              <div className="p-2 bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 rounded-lg">
                <Bell size={20} />
              </div>
              <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">Notification Hub</h2>
            </div>
            <div className="p-8 space-y-8">
              <div className="space-y-4">
                {[
                  { title: 'Weekly Audit Digest', desc: 'Get a summary of all flagged risks every Monday.' },
                  { title: 'Critical Alert Pings', desc: 'Instant email when a "High" severity risk is found.' },
                  { title: 'Team Tagging', desc: 'Notify me when someone tags me in a documented note.' },
                ].map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center py-3 border-b border-slate-100 dark:border-slate-800 last:border-0">
                    <div>
                      <p className="font-semibold text-slate-800 dark:text-slate-200">{item.title}</p>
                      <p className="text-sm text-slate-500 dark:text-slate-400">{item.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked={idx !== 0} />
                      <div className="w-11 h-6 bg-slate-200 dark:bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 dark:after:border-slate-600 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                ))}
              </div>
              <div className="pt-6 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3">
                <button className="px-5 py-2.5 bg-blue-600 text-white font-medium hover:bg-blue-700 rounded-lg transition-colors shadow-sm">
                  Save Preferences
                </button>
              </div>
            </div>
          </>
        );

      case 'appearance':
        return (
          <>
            <div className="px-8 py-6 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3">
              <div className="p-2 bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 rounded-lg">
                <Moon size={20} />
              </div>
              <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">Appearance</h2>
            </div>
            <div className="p-8 space-y-8">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Theme Preference</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div
                    onClick={() => switchTheme('light')}
                    className={`border-2 ${
                      theme === 'light' ? 'border-blue-600' : 'border-slate-200 dark:border-slate-700'
                    } bg-white dark:bg-slate-800 p-4 rounded-xl cursor-pointer hover:border-blue-500`}
                  >
                    <div className="h-20 bg-slate-100 rounded mb-3 flex flex-col gap-2 p-2 border border-slate-200">
                      <div className="w-1/2 h-3 bg-slate-200 rounded"></div>
                      <div className="w-full h-8 bg-white rounded"></div>
                    </div>
                    <p className="text-center font-semibold text-slate-800 dark:text-white text-sm">Light Mode</p>
                  </div>
                  <div
                    onClick={() => switchTheme('dark')}
                    className={`border-2 ${
                      theme === 'dark' ? 'border-blue-600' : 'border-slate-200 dark:border-slate-700'
                    } bg-slate-900 p-4 rounded-xl cursor-pointer hover:border-blue-500`}
                  >
                    <div className="h-20 bg-slate-800 rounded mb-3 flex flex-col gap-2 p-2 border border-slate-700">
                      <div className="w-1/2 h-3 bg-slate-700 rounded"></div>
                      <div className="w-full h-8 bg-slate-950 border border-slate-700 rounded"></div>
                    </div>
                    <p className="text-center font-semibold text-white text-sm">Dark Mode</p>
                  </div>
                  <div
                    onClick={() => switchTheme('system')}
                    className={`border-2 ${
                      theme === 'system' ? 'border-blue-600' : 'border-slate-200 dark:border-slate-700'
                    } bg-white dark:bg-slate-800 p-4 rounded-xl cursor-pointer hover:border-blue-500`}
                  >
                    <div className="h-20 bg-gradient-to-br from-slate-100 to-slate-800 rounded mb-3 border border-slate-300 dark:border-slate-600"></div>
                    <p className="text-center font-semibold text-slate-800 dark:text-white text-sm">System Default</p>
                  </div>
                </div>
              </div>
            </div>
          </>
        );

      case 'profile':
      default:
        return (
          <>
            <div className="px-8 py-6 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3">
              <div className="p-2 bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 rounded-lg">
                <User size={20} />
              </div>
              <h2 className="text-xl font-bold text-slate-800 dark:text-slate-100">Profile Information</h2>
            </div>

            <div className="p-8 space-y-8">
              {statusMsg.text && (
                <div
                  className={`p-4 rounded-xl flex items-center gap-3 text-sm font-semibold border ${
                    statusMsg.type === 'success'
                      ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300'
                      : 'bg-red-50 dark:bg-red-950/40 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300'
                  }`}
                >
                  {statusMsg.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
                  <span>{statusMsg.text}</span>
                </div>
              )}

              <div className="flex items-center gap-6">
                <img
                  src={`https://ui-avatars.com/api/?name=${encodeURIComponent(
                    profileData.name || 'User'
                  )}&background=eff6ff&color=2563eb&size=100`}
                  alt="Profile"
                  className="w-24 h-24 rounded-full border-4 border-white dark:border-slate-800 shadow-md"
                />
                <div>
                  <h3 className="text-lg font-semibold text-slate-800 dark:text-white">{user?.name || 'User'}</h3>
                  <p className="text-slate-500 dark:text-slate-400 mb-3">{user?.role || 'Researcher'}</p>
                </div>
              </div>

              <form onSubmit={handleProfileSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Full Name</label>
                    <input
                      type="text"
                      value={profileData.name}
                      onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                      required
                      className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:text-white transition-all"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Email Address (Read-only)</label>
                    <input
                      type="email"
                      value={user?.email || ''}
                      disabled
                      className="w-full px-4 py-2.5 bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-500 dark:text-slate-400 cursor-not-allowed"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Role / Title</label>
                  <select
                    value={profileData.role}
                    onChange={(e) => setProfileData({ ...profileData, role: e.target.value })}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:text-white transition-all"
                  >
                    <option value="Researcher">Researcher</option>
                    <option value="Lawyer">Lawyer</option>
                    <option value="Student">Student</option>
                    <option value="Professional">Professional</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div className="pt-6 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-5 py-2.5 bg-blue-600 text-white font-medium hover:bg-blue-700 rounded-lg transition-colors shadow-sm flex items-center gap-2 cursor-pointer disabled:opacity-50"
                  >
                    {isLoading && <Loader2 size={16} className="animate-spin" />}
                    Save Changes
                  </button>
                </div>
              </form>
            </div>
          </>
        );
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">Settings</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-1">Manage your account preferences and security settings</p>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        <div className="w-full md:w-64 space-y-1 shrink-0">
          <button
            onClick={() => {
              setActiveTab('profile');
              setStatusMsg({ type: '', text: '' });
            }}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors text-left cursor-pointer ${
              activeTab === 'profile'
                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <User size={18} />
            Profile Settings
          </button>
          <button
            onClick={() => {
              setActiveTab('security');
              setStatusMsg({ type: '', text: '' });
            }}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors text-left cursor-pointer ${
              activeTab === 'security'
                ? 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <Lock size={18} />
            Security
          </button>
          <button
            onClick={() => {
              setActiveTab('notifications');
              setStatusMsg({ type: '', text: '' });
            }}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors text-left cursor-pointer ${
              activeTab === 'notifications'
                ? 'bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <Bell size={18} />
            Notifications
          </button>
          <button
            onClick={() => {
              setActiveTab('appearance');
              setStatusMsg({ type: '', text: '' });
            }}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors text-left cursor-pointer ${
              activeTab === 'appearance'
                ? 'bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <Moon size={18} />
            Appearance
          </button>
        </div>

        <div className="flex-1 bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden h-fit transition-colors duration-200">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default Settings;
