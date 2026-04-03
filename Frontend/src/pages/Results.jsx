import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Clock, CheckCircle2, AlertCircle, ExternalLink, Loader2, RefreshCcw, Trash2, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getAllJobs, getJobStatus, deleteJob } from '../services/api';

const Results = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [jobToDelete, setJobToDelete] = useState(null); // Stores the job object to delete
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchJobs = async () => {
    try {
      const response = await getAllJobs();
      setJobs(response.data);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const confirmDelete = async () => {
    if (!jobToDelete) return;
    setIsDeleting(true);
    try {
      await deleteJob(jobToDelete.jobId);
      setJobs(jobs.filter(j => j.jobId !== jobToDelete.jobId));
      setJobToDelete(null);
    } catch (err) {
      alert('Failed to purge job: ' + (err.response?.data?.error || err.message));
    } finally {
      setIsDeleting(false);
    }
  };

  useEffect(() => {
    fetchJobs();

    // Poll for status updates every 5 seconds
    const interval = setInterval(() => {
      fetchJobs();
    }, 5000);

    return () => clearInterval(interval);
  }, []); // Only run once on mount

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="relative">
          <div className="w-12 h-12 border-t-2 border-primary rounded-full animate-spin"></div>
          <Loader2 className="w-6 h-6 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-primary animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in relative">
      <div className="flex items-center justify-between mb-10">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Intelligence Ledger</h2>
          <p className="text-slate-500 mt-1">Track all your YouTube knowledge extraction jobs here.</p>
        </div>
        <button 
          onClick={fetchJobs}
          className="p-2 hover:bg-white/5 rounded-lg transition-colors border border-card-border group"
        >
          <RefreshCcw className="w-5 h-5 text-slate-400 group-hover:rotate-180 transition-transform duration-500" />
        </button>
      </div>

      {jobs.length === 0 ? (
        <div className="glass-card flex flex-col items-center justify-center text-center py-20">
          <div className="p-4 bg-slate-400/5 rounded-full mb-6">
            <ClipboardList className="w-12 h-12 text-slate-600" />
          </div>
          <h3 className="text-xl font-medium mb-2">No jobs found</h3>
          <p className="text-slate-500 mb-8 max-w-sm">
            You haven't generated any documents yet. Paste a YouTube URL to get started.
          </p>
          <Link to="/" className="btn-primary">
            Start Generating
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <VideoCard 
              key={job.jobId} 
              job={job} 
              onDelete={() => setJobToDelete(job)} 
            />
          ))}
        </div>
      )}

      {/* Custom Confirmation Modal */}
      <AnimatePresence>
        {jobToDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setJobToDelete(null)}
              className="absolute inset-0 bg-background/80 backdrop-blur-md"
            />
            
            <motion.div 
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              className="glass-card max-w-md w-full relative z-10 p-8 border-red-500/20 shadow-2xl shadow-red-500/5"
            >
              <div className="mb-6">
                <div className="w-12 h-12 bg-red-500/10 rounded-full flex items-center justify-center mb-4 border border-red-500/20">
                  <Trash2 className="w-6 h-6 text-red-500" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Initialize Deletion Sequence?</h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  You are about to purge the extracted intelligence for <span className="text-slate-200 font-medium">"{jobToDelete.title || 'this video'}"</span>. This action is permanent and cannot be reversed.
                </p>
              </div>

              <div className="flex gap-3">
                <button 
                  onClick={() => setJobToDelete(null)}
                  className="flex-1 px-4 py-3 bg-white/5 hover:bg-white/10 text-white font-medium rounded-lg border border-white/5 transition-all text-sm"
                  disabled={isDeleting}
                >
                  Cancel
                </button>
                <button 
                  onClick={confirmDelete}
                  className="flex-2 px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-lg transition-all text-sm flex items-center justify-center gap-2"
                  disabled={isDeleting}
                >
                  {isDeleting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                  {isDeleting ? 'Purging...' : 'Confirm Purge'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

const VideoCard = ({ job, onDelete }) => {
  const isCompleted = job.status === 'completed';
  const isFailed = job.status === 'failed';
  const isActive = job.status === 'active';

  return (
    <div className="glass-card p-0 overflow-hidden hover:scale-[1.02] hover:shadow-2xl hover:shadow-primary/5 transition-all duration-300 group flex flex-col h-full border-white/[0.03]">
      <div className="relative aspect-video">
        <img 
          src={job.thumbnail} 
          alt={job.title || "YouTube Video"} 
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background/90 to-transparent flex items-end p-4">
          <div className="flex-1">
             <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
               ID: {job.jobId}
             </span>
             <h3 className="font-semibold text-white truncate line-clamp-1">
               {job.title || 'Processing...'}
             </h3>
          </div>
        </div>
        
        {/* Status Badge */}
        <div className="absolute top-3 right-3">
          <div className={`px-3 py-1 rounded-full text-[10px] font-bold border backdrop-blur-md flex items-center gap-1.5 ${
            isCompleted ? 'bg-green-500/10 text-green-400 border-green-500/20' :
            isFailed ? 'bg-red-500/10 text-red-400 border-red-500/20' :
            'bg-primary/10 text-primary-light border-primary/20'
          }`}>
            {isCompleted ? <CheckCircle2 className="w-3 h-3" /> :
             isFailed ? <AlertCircle className="w-3 h-3" /> :
             <Loader2 className="w-3 h-3 animate-spin" />}
            <span className="uppercase">{job.status}</span>
          </div>
        </div>

        {/* Delete Button - Appears on Hover */}
        <div className="absolute top-3 left-3 group-hover:transition-all duration-300">
          <button 
            onClick={(e) => {
              e.preventDefault();
              onDelete();
            }}
            className="p-2 bg-black/40 hover:bg-red-500/40 text-white/70 hover:text-white rounded-full border border-white/10 backdrop-blur-md transition-all shadow-lg"
            title="Delete Intelligence"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="p-5 flex-1 flex flex-col justify-between">
        <div className="space-y-3 mb-6">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Clock className="w-3.5 h-3.5" />
            <span>{new Date(parseInt(job.createdAt)).toLocaleString()}</span>
          </div>
          {isFailed && (
            <p className="text-xs text-red-400 bg-red-400/5 p-2 rounded border border-red-400/10 italic truncate">
              {job.error || 'Unknown error'}
            </p>
          )}
        </div>

        {isCompleted ? (
          <Link 
            to={`/result/${job.jobId}`} 
            className="btn-primary w-full text-sm inline-flex items-center justify-center gap-2 py-3"
          >
            <ExternalLink className="w-4 h-4" />
            <span>View Intelligence</span>
          </Link>
        ) : (
          <div className="w-full py-3 bg-slate-400/5 text-slate-500 text-sm font-medium rounded-lg text-center border border-card-border/50">
             {isActive ? 'Synthesizing...' : 'Waiting in Queue...'}
          </div>
        )}
      </div>
    </div>
  );
};

// Placeholder icon
const ClipboardList = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
    <path d="M12 11h4" />
    <path d="M12 16h4" />
    <path d="M8 11h.01" />
    <path d="M8 16h.01" />
  </svg>
);

export default Results;
