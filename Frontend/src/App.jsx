import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Generate from './pages/Generate';
import Results from './pages/Results';
import Viewer from './pages/Viewer';

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-background text-foreground bg-[radial-gradient(circle_at_top_right,rgba(59,130,246,0.08),transparent_40%)]">
        <Navbar />
        
        <main className="flex-1 md:ml-64 p-8">
          <div className="max-w-6xl mx-auto">
            <Routes>
              <Route path="/" element={<Generate />} />
              <Route path="/jobs" element={<Results />} />
              <Route path="/result/:jobId" element={<Viewer />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
