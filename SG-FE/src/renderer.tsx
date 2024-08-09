import React, { useEffect, useState } from 'react';
import axios from 'axios';
import logger from './logger';  // Assuming this is the correct path to your logger file
import io from 'socket.io-client';

const socket = io('https://localhost:5000', {
    secure: true,
    rejectUnauthorized: false  // This is fine for development; for production, use a valid certificate
});

const App: React.FC = () => {
    const [status, setStatus] = useState<string>('Loading...');
    const [policies, setPolicies] = useState<any>(null);

    useEffect(() => {
        logger.info('Application started');  // Move logger inside useEffect to ensure it only logs when component mounts

        socket.on('policy_update', (updatedPolicies) => {
            setPolicies(updatedPolicies);
            logger.info('Policies updated', updatedPolicies);
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
            }
        };
    
        fetchPolicies();
    }, []);
    
    return (
        <div>
            <h1>Welcome to SecureNetGuard</h1>
            <div id="status">{status}</div>
            <div>Policies: {policies ? JSON.stringify(policies) : 'No policies loaded'}</div>
        </div>
    );
};

export default App;