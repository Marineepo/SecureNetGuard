import axios from 'axios';

const api = axios.create({
    baseURL: 'https://localhost:5000',  // will change this to our backend URL
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
    }
});

export default api;