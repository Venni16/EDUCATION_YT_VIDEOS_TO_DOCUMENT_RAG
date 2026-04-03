import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { FileText, Download, ChevronLeft, Calendar, User, Zap, Globe, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import { getJobResult } from '../services/api';

const Viewer = () => {
  const { jobId } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const response = await getJobResult(jobId);
        setResult(response.data);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load result. Perhaps it is still being processed?');
      } finally {
        setLoading(false);
      }
    };
    fetchResult();
  }, [jobId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <p className="text-slate-500 font-medium">Reconstructing Intelligence...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card flex flex-col items-center justify-center text-center py-20 max-w-2xl mx-auto mt-10 border-red-500/10">
        <div className="p-4 bg-red-400/5 rounded-full mb-6">
          <AlertCircle className="w-12 h-12 text-red-400" />
        </div>
        <h3 className="text-2xl font-bold mb-2">Access Denied</h3>
        <p className="text-slate-500 mb-8 max-w-sm">
          {error}
        </p>
        <Link to="/jobs" className="btn-primary flex items-center gap-2">
          <ChevronLeft className="w-4 h-4" />
          Back to Ledger
        </Link>
      </div>
    );
  }

  return (
    <div className="animate-fade-in max-w-5xl mx-auto pb-24">
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-10">
        <Link to="/jobs" className="group flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm font-medium">
          <div className="p-2 rounded-lg bg-white/5 border border-white/5 group-hover:bg-primary/10 group-hover:border-primary/20 transition-all">
            <ChevronLeft className="w-4 h-4" />
          </div>
          Return to Ledger
        </Link>
        <div className="flex gap-4">
           {result.pdf_url && (
             <a 
               href={`http://localhost:8000${result.pdf_url}`} 
               target="_blank"
               rel="noopener noreferrer"
               download
               className="btn-primary inline-flex items-center gap-2 px-5 py-2.5 text-sm"
             >
               <Download className="w-4 h-4" />
               Download PDF
             </a>
           )}
        </div>
      </div>

      {/* Hero Section */}
      <div className="glass-card p-8 mb-12 border-primary/10 relative overflow-hidden group">
        <div className="absolute top-0 right-0 p-8 opacity-5 transition-opacity group-hover:opacity-10">
           <Zap className="w-48 h-48 text-primary shadow-2xl" fill="currentColor" />
        </div>
        
        <div className="flex flex-col md:flex-row gap-10 relative z-10">
          <div className="w-full md:w-64 shrink-0 rounded-xl overflow-hidden shadow-2xl shadow-black/50 border border-white/5">
            <img 
              src={result.thumbnail_url} 
              alt={result.title} 
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1 py-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary-light text-[10px] font-bold uppercase tracking-widest mb-6">
              <Sparkles className="w-3 h-3" />
              <span>Verified Report</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6 leading-tight">
              {result.title}
            </h1>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="flex items-center gap-3">
                <Calendar className="w-4 h-4 text-slate-500" />
                <div className="text-[10px]">
                  <p className="text-slate-600 uppercase font-bold tracking-tighter">Date</p>
                  <p className="font-medium">Recent</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <User className="w-4 h-4 text-slate-500" />
                <div className="text-[10px]">
                  <p className="text-slate-600 uppercase font-bold tracking-tighter">Provider</p>
                  <p className="font-medium">Vortex AI</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Globe className="w-4 h-4 text-slate-500" />
                <div className="text-[10px]">
                  <p className="text-slate-600 uppercase font-bold tracking-tighter">Source</p>
                  <p className="font-medium">YouTube</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <FileText className="w-4 h-4 text-slate-500" />
                <div className="text-[10px]">
                  <p className="text-slate-600 uppercase font-bold tracking-tighter">Length</p>
                  <p className="font-medium">Extensive</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Markdown Content */}
      <div className="glass-card p-10 prose prose-invert prose-slate max-w-none prose-headings:tracking-tight prose-headings:font-bold prose-a:text-primary-light">
        <ReactMarkdown 
          components={{
            h1: ({node, ...props}) => <h1 className="text-4xl mt-0 mb-8 border-b border-white/5 pb-4" {...props} />,
            h2: ({node, ...props}) => <h2 className="text-2xl mt-12 mb-6 text-primary-light" {...props} />,
            h3: ({node, ...props}) => <h3 className="text-xl mt-8 mb-4 font-semibold text-slate-200" {...props} />,
            blockquote: ({node, ...props}) => (
              <blockquote className="border-l-4 border-primary/30 bg-primary/5 p-6 rounded-r-xl my-8 italic" {...props} />
            ),
            ul: ({node, ...props}) => <ul className="space-y-3 my-6 list-disc pl-6" {...props} />,
            code: ({node, inline, className, children, ...props}) => (
              <code className={`${inline ? 'bg-slate-800 text-slate-200 px-1.5 py-0.5 rounded text-sm' : 'block bg-slate-900 border border-white/5 p-4 rounded-xl my-6 text-sm overflow-x-auto'}`} {...props}>
                {children}
              </code>
            )
          }}
        >
          {result.document}
        </ReactMarkdown>
      </div>
    </div>
  );
};

export default Viewer;
