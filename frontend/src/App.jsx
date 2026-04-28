import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Shopping from './pages/Shopping';
import Planner from './pages/Planner';

export default function App() {
  return (
    <Router>
      <div className="relative min-h-screen">
        <div className="grain" />
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/shopping" element={<Shopping />} />
          <Route path="/planner" element={<Planner />} />
        </Routes>
      </div>
    </Router>
  );
}