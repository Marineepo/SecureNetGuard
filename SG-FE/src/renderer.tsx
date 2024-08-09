import React, { useEffect, useState } from 'react';
import axios from 'axios';
import logger from './logger';
import io from 'socket.io-client';
import LogRocket from 'logrocket';

LogRocket.init('your-app-id');

const socket = io('https://localhost:5000', {
    secure: true,
    rejectUnauthorized: false  // for self-signed certificates
});

const App: React.FC = () => {
    const [status, setStatus] = useState<string>('Loading...');
    const [policies, setPolicies] = useState<any>(null);
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string>('');

    useEffect(() => {
        logger.info('Application started');

        socket.on('policy_update', (updatedPolicies) => {
            setPolicies(updatedPolicies);
        });

        return () => {
            socket.off('policy_update');
        };
    }, []);

    useEffect(() => {
        const fetchPolicies = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                setStatus('Not authenticated');
                return;
            }

            try {
                const response = await axios.get('https://localhost:5000/api/policies', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setPolicies(response.data);
                setStatus('Policies Loaded');
            } catch (error) {
                setStatus('Failed to load policies');
                logger.error('Failed to load policies', error);
            }
        };

        fetchPolicies();
    }, [isAuthenticated]);

    const handleLogin = async () => {
        try {
            const response = await axios.post('https://localhost:5000/api/login', {
                username,
                password
            });
            localStorage.setItem('token', response.data.access_token);
            setIsAuthenticated(true);
            setError('');
        } catch (error) {
            setError('Invalid credentials');
            logger.error('Login failed', error);
        }
    };

    return (
        <div>
            {!isAuthenticated ? (
                <div>
                    <input 
                        type="text" 
                        value={username} 
                        onChange={(e) => setUsername(e.target.value)} 
                        placeholder="Username" 
                    />
                    <input 
                        type="password" 
                        value={password} 
                        onChange={(e) => setPassword(e.target.value)} 
                        placeholder="Password" 
                    />
                    <button onClick={handleLogin}>Login</button>
                    {error && <p>{error}</p>}
                </div>
            ) : (
                <div>
                    <h1>Welcome to SecureNetGuard</h1>
                    <div id="status">Policies Loaded: {JSON.stringify(policies)}</div>
                </div>
            )}
        </div>
    );
};

export default App;