import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import AuthForm from '../components/AuthForm';
import type { FormEvent } from 'react';
const SignupPage = () => {
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');
  const [error, setError] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const { signup } = useAuth();
  const navigate = useNavigate();

  const validatePasswords = () => {
    if (password !== repeatPassword) {
      setPasswordError('Passwords do not match');
      return false;
    }
    setPasswordError('');
    return true;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validatePasswords()) {
      return;
    }

    setError(''); // Clear any previous errors
    try {
      await signup(name, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Failed to create an account');
    }
  };

  return (
    <Layout>
      <AuthForm
        title="Create your account"
        buttonText="Sign up"
        error={error}
        passwordError={passwordError}
        name={name}
        setName={setName}
        password={password}
        setPassword={setPassword}
        repeatPassword={repeatPassword}
        setRepeatPassword={setRepeatPassword}
        onRepeatPasswordBlur={validatePasswords}
        onSubmit={handleSubmit}
        footerText="Already have an account?"
        footerLinkText="Sign in"
        footerLinkTo="/login"
      />
    </Layout>
  );
};

export default SignupPage;