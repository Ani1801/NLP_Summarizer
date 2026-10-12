import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Scale, Loader2, AlertCircle, UserPlus, ArrowRight } from 'lucide-react';

/* ─────────────────────────────────────────────
   Google Identity Services button component.
   Renders the official Google Sign-In button
   and calls onSuccess(credential) on success.
   ───────────────────────────────────────────── */
const GoogleSignInButton = ({ onSuccess, onError, disabled }) => {
  const containerRef = useRef(null);
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  useEffect(() => {
    if (!clientId || clientId === 'your-google-client-id.apps.googleusercontent.com') return;

    const initGoogle = () => {
      if (!window.google?.accounts?.id) return;
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response) => {
          if (response.credential) {
            onSuccess(response.credential);
          } else {
            onError('Google sign-in was cancelled or failed.');
          }
        },
        auto_select: false,
        cancel_on_tap_outside: true,
      });
      if (containerRef.current) {
        window.google.accounts.id.renderButton(containerRef.current, {
          theme: 'outline',
          size: 'large',
          width: containerRef.current.offsetWidth || 400,
          text: 'continue_with',
          shape: 'rectangular',
        });
      }
    };

    // Load the Google Identity Services script if not already present
    if (window.google?.accounts?.id) {
      initGoogle();
    } else {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initGoogle;
      document.head.appendChild(script);
    }
  }, [clientId, onSuccess, onError]);

  if (!clientId || clientId === 'your-google-client-id.apps.googleusercontent.com') {
    return (
      <div className="w-full py-2.5 px-4 border border-dashed border-slate-300 dark:border-slate-600 rounded-xl text-xs text-slate-500 dark:text-slate-400 text-center font-medium">
        Google Sign-In not configured — set{' '}
        <code className="font-mono bg-slate-100 dark:bg-slate-700 px-1 rounded">VITE_GOOGLE_CLIENT_ID</code> to enable
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`w-full flex justify-center transition-opacity ${disabled ? 'opacity-50 pointer-events-none' : ''}`}
      style={{ minHeight: 44 }}
    />
  );
};

/* ─────────────────────────────────────────────
   Main Auth page
   ───────────────────────────────────────────── */
const Auth = () => {
  const [searchParams] = useSearchParams();
  const initialMode = searchParams.get('mode') === 'signup' ? false : true;

  const [isLogin, setIsLogin] = useState(initialMode);
  const { login, signup, googleLogin, isLoading } = useAuth();
  const navigate = useNavigate();
  const nameInputRef = useRef(null);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'Researcher',
  });
  const [errors, setErrors] = useState({});
  const [accountNotFound, setAccountNotFound] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  useEffect(() => {
    const mode = searchParams.get('mode');
    if (mode === 'signup') setIsLogin(false);
    else if (mode === 'login') setIsLogin(true);
  }, [searchParams]);

  const validate = () => {
    const newErrors = {};
    if (!isLogin && !formData.name.trim()) newErrors.name = 'Full name is required';
    if (!formData.email.trim()) newErrors.email = 'Email address is required';
    else if (!/^\S+@\S+\.\S+$/.test(formData.email.trim()))
      newErrors.email = 'Please enter a valid email address';
    if (!formData.password) newErrors.password = 'Password is required';
    else if (formData.password.length < 6)
      newErrors.password = 'Password must be at least 6 characters';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setAccountNotFound(false);
    if (!validate()) return;
    try {
      if (isLogin) {
        await login(formData.email.trim(), formData.password);
      } else {
        await signup(formData.name.trim(), formData.email.trim(), formData.password, formData.role);
      }
      navigate('/dashboard');
    } catch (err) {
      const errMsg = err.message || '';
      if (
        isLogin &&
        (errMsg.toLowerCase().includes('account does not exist') ||
          errMsg.includes('404') ||
          errMsg.toLowerCase().includes('not found'))
      ) {
        setAccountNotFound(true);
        setErrors({ form: 'No account found with this email address.' });
      } else {
        setErrors({ form: errMsg });
      }
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: '' });
    if (accountNotFound) setAccountNotFound(false);
  };

  const switchToSignup = () => {
    setIsLogin(false);
    setErrors({});
    setAccountNotFound(false);
    setTimeout(() => nameInputRef.current?.focus(), 100);
  };

  /* ── Google auth handlers ── */
  const handleGoogleSuccess = async (credential) => {
    setGoogleLoading(true);
    setErrors({});
    try {
      await googleLogin(credential);
      navigate('/dashboard');
    } catch (err) {
      setErrors({ form: err.message || 'Google sign-in failed. Please try again.' });
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleGoogleError = (msg) => {
    if (msg) setErrors({ form: msg });
  };

  const anyLoading = isLoading || googleLoading;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans w-full absolute top-0 left-0 z-50 text-slate-900 dark:text-slate-100 transition-colors duration-200">
      {/* Ambient blur */}
      <div className="absolute top-10 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-500/10 dark:bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md flex flex-col items-center relative z-10">
        <div className="w-14 h-14 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-blue-500/20">
          <Scale size={28} className="text-white" />
        </div>
        <h2 className="text-center text-3xl font-extrabold tracking-tight">
          {isLogin ? 'Sign in to DocSummarizer' : 'Create your account'}
        </h2>
        <p className="mt-2.5 text-center text-sm text-slate-600 dark:text-slate-400 font-medium">
          {isLogin ? "Don't have an account yet? " : 'Already registered? '}
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setErrors({});
              setAccountNotFound(false);
            }}
            className="font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
          >
            {isLogin ? 'Create an account' : 'Sign in here'}
          </button>
        </p>
      </div>

      {/* Card */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="bg-white dark:bg-slate-800/90 backdrop-blur-sm py-8 px-4 shadow-xl shadow-slate-200/50 dark:shadow-none sm:rounded-2xl sm:px-10 border border-slate-200/80 dark:border-slate-700/60">

          {/* Google button section */}
          <div className="mb-6">
            <GoogleSignInButton
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              disabled={anyLoading}
            />
            {googleLoading && (
              <div className="flex items-center justify-center gap-2 mt-3 text-sm text-slate-500 dark:text-slate-400">
                <Loader2 size={16} className="animate-spin" />
                Signing in with Google…
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200 dark:border-slate-700" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-3 bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-medium text-xs tracking-wide uppercase">
                or continue with email
              </span>
            </div>
          </div>

          {/* Account not found banner */}
          {accountNotFound && (
            <div className="mb-6 p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-amber-800 dark:text-amber-200 space-y-3">
              <div className="flex items-start gap-2.5">
                <AlertCircle size={20} className="shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
                <div>
                  <h4 className="text-sm font-bold">Account Not Found</h4>
                  <p className="text-xs font-medium mt-0.5 text-amber-700 dark:text-amber-300">
                    No account exists for{' '}
                    <span className="font-semibold text-amber-900 dark:text-amber-100">
                      {formData.email}
                    </span>
                    . You can create one right now.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={switchToSignup}
                className="w-full mt-2 py-2 px-3 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-sm shadow-amber-600/20"
              >
                <UserPlus size={15} />
                Create Account for {formData.email}
                <ArrowRight size={14} />
              </button>
            </div>
          )}

          {/* Generic form error */}
          {errors.form && !accountNotFound && (
            <div className="mb-5 p-3.5 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/60 flex items-start gap-2.5 text-sm text-red-600 dark:text-red-400 font-medium">
              <AlertCircle size={18} className="shrink-0 mt-0.5" />
              <span>{errors.form}</span>
            </div>
          )}

          {/* Email/password form */}
          <form className="space-y-4 font-sans" onSubmit={handleSubmit}>
            {!isLogin && (
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  Full Name
                </label>
                <input
                  ref={nameInputRef}
                  name="name"
                  type="text"
                  value={formData.name}
                  onChange={handleChange}
                  className={`appearance-none block w-full px-3.5 py-2.5 border ${
                    errors.name
                      ? 'border-red-400 focus:ring-red-100 bg-red-50 dark:bg-red-950/20'
                      : 'border-slate-300 dark:border-slate-600 focus:border-blue-500 focus:ring-blue-100 dark:focus:ring-blue-900/30 bg-white dark:bg-slate-900'
                  } rounded-xl shadow-sm placeholder-slate-400 focus:outline-none focus:ring-4 sm:text-sm transition-all`}
                  placeholder="Jane Doe"
                />
                {errors.name && (
                  <p className="mt-1 text-xs font-semibold text-red-600 dark:text-red-400">
                    {errors.name}
                  </p>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Email address
              </label>
              <input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                className={`appearance-none block w-full px-3.5 py-2.5 border ${
                  errors.email
                    ? 'border-red-400 focus:ring-red-100 bg-red-50 dark:bg-red-950/20'
                    : 'border-slate-300 dark:border-slate-600 focus:border-blue-500 focus:ring-blue-100 dark:focus:ring-blue-900/30 bg-white dark:bg-slate-900'
                } rounded-xl shadow-sm placeholder-slate-400 focus:outline-none focus:ring-4 sm:text-sm transition-all`}
                placeholder="name@firm.com"
              />
              {errors.email && (
                <p className="mt-1 text-xs font-semibold text-red-600 dark:text-red-400">
                  {errors.email}
                </p>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300">
                  Password
                </label>
                {isLogin && (
                  <a
                    href="#"
                    className="font-semibold text-blue-600 dark:text-blue-400 hover:underline text-xs"
                  >
                    Forgot Password?
                  </a>
                )}
              </div>
              <input
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                className={`appearance-none block w-full px-3.5 py-2.5 border ${
                  errors.password
                    ? 'border-red-400 focus:ring-red-100 bg-red-50 dark:bg-red-950/20'
                    : 'border-slate-300 dark:border-slate-600 focus:border-blue-500 focus:ring-blue-100 dark:focus:ring-blue-900/30 bg-white dark:bg-slate-900'
                } rounded-xl shadow-sm placeholder-slate-400 focus:outline-none focus:ring-4 sm:text-sm transition-all`}
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-xs font-semibold text-red-600 dark:text-red-400">
                  {errors.password}
                </p>
              )}
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                  Your Role
                </label>
                <div className="relative">
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    className="appearance-none block w-full pl-3.5 pr-10 py-2.5 border border-slate-300 dark:border-slate-600 rounded-xl shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30 focus:border-blue-500 sm:text-sm transition-all bg-white dark:bg-slate-900 font-medium text-slate-700 dark:text-slate-200"
                  >
                    <option value="Researcher">Researcher</option>
                    <option value="Student">Student</option>
                    <option value="Professional">Professional</option>
                    <option value="Other">Other</option>
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>
            )}

            <div className="pt-3">
              <button
                type="submit"
                disabled={anyLoading}
                className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl shadow-md text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200 dark:focus:ring-blue-900/50 transition-all disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
              >
                {isLoading ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : isLogin ? (
                  'Sign in'
                ) : (
                  'Create Account'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Auth;
