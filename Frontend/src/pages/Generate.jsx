import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Youtube, Search, Loader2, AlertCircle, ArrowRight } from 'lucide-react';
import { generateDoc } from '../services/api';

const Generate = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError(null);

    try {
      const response = await generateDoc(url);
      console.log('Job Created:', response.data);
      // Wait a bit then navigate to jobs or poll here? 
      // The plan says "After submit: Display Job ID, Show status".
      // Let's navigate to the jobs page so the user can see it in their list.
      navigate('/jobs');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start generation. Is the backend running?');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center animate-fade-in">
      <div className="w-full max-w-2xl text-center mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary-light text-xs font-bold uppercase tracking-widest mb-6">
          <Zap className="w-3 h-3" />
          <span>Next-Gen Knowledge Extraction</span>
        </div>
        <h2 className="text-5xl font-bold mb-6 tracking-tight leading-tight">
          Turn any YouTube video into <br />
          <span className="bg-gradient-to-r from-primary to-accent-neon bg-clip-text text-transparent">
            Structured Intelligence.
          </span>
        </h2>
        <p className="text-slate-400 text-lg max-w-lg mx-auto">
          Paste a YouTube URL below to extract transcripts, generate summaries, and build a local RAG document in seconds.
        </p>
      </div>

      <div className="w-full max-w-xl group">
        <form onSubmit={handleSubmit} className="relative">
          <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-primary transition-colors">
            <Youtube className="w-6 h-6" />
          </div>
          <input
            type="text"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full bg-card/50 border border-card-border hover:border-primary/50 focus:border-primary focus:ring-4 focus:ring-primary/10 rounded-2xl py-5 pl-14 pr-32 outline-none transition-all text-lg placeholder:text-slate-600 backdrop-blur-xl group-hover:shadow-2xl group-hover:shadow-primary/5"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !url}
            className="absolute right-2.5 top-2.5 btn-primary py-2.5 px-6 flex items-center gap-2 disabled:opacity-50 disabled:active:scale-100"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <span>Generate</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="mt-4 flex items-start gap-2 text-red-400 bg-red-400/5 p-4 rounded-xl border border-red-400/20 animate-slide-up">
            <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        <div className="mt-12 flex flex-wrap justify-center gap-8 text-slate-500 opacity-60">
          <div className="flex items-center gap-2 grayscale hover:grayscale-0 transition-all cursor-default">
            <Zap className="w-4 h-4" />
            <span className="text-xs font-medium">FastAPI Engine</span>
          </div>
          <div className="flex items-center gap-2 grayscale hover:grayscale-0 transition-all cursor-default">
            <Search className="w-4 h-4" />
            <span className="text-xs font-medium">Auto-Chunking</span>
          </div>
          <div className="flex items-center gap-2 grayscale hover:grayscale-0 transition-all cursor-default">
            <FileText className="w-4 h-4" />
            <span className="text-xs font-medium">MD + PDF Output</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Placeholder icons if not imported
const Zap = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
  </svg>
);
const FileText = ({ className }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
    <line x1="10" y1="9" x2="8" y2="9" />
  </svg>
);

export default Generate;
