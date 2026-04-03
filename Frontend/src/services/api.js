import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:3000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const generateDoc = (url) => api.post('/generate', { url });
export const getJobStatus = (jobId) => api.get(`/status/${jobId}`);
export const getJobResult = (jobId) => api.get(`/result/${jobId}`);
export const getAllJobs = () => api.get('/all-jobs');
export const deleteJob = (jobId) => api.delete(`/job/${jobId}`);

export default api;
