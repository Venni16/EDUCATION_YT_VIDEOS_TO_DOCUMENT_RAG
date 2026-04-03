import { Link, useLocation } from 'react-router-dom';
import { Home, ClipboardList, PlusCircle, Zap } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { name: 'Generate', path: '/', icon: PlusCircle },
    { name: 'My Jobs', path: '/jobs', icon: ClipboardList },
  ];

  return (
    <nav className="fixed left-0 top-0 h-full w-64 bg-card border-r border-card-border p-6 hidden md:block">
      <div className="flex items-center gap-3 mb-12 px-2">
        <div className="p-2 bg-primary rounded-lg shadow-lg shadow-primary/20">
          <Zap className="text-white w-6 h-6" fill="currentColor" />
        </div>
        <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
          Vortex RAG
        </h1>
      </div>

      <div className="space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={twMerge(clsx(
                "nav-link",
                isActive && "active bg-primary/10 text-primary-light"
              ))}
            >
              <Icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      <div className="absolute bottom-8 left-6 right-6">
        <div className="glass-card bg-primary-dark/5 p-4 text-xs text-slate-500 rounded-xl leading-relaxed">
          <p className="font-medium text-slate-400 mb-1">Status: Operational</p>
          <p>AI Service v1.0.4 connected</p>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
