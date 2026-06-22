const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:80/'
    : '/api';

export { API_URL };