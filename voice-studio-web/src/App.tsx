import { Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ModelSelectPage from "./pages/ModelSelectPage";
import TurboPage from "./pages/TurboPage";
import MultilingualPage from "./pages/MultilingualPage";

export default function App() {
  return (
    <div className="app">
      <nav className="nav">
        <Link to="/">Home</Link>
        <Link to="/models">Models</Link>
      </nav>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/models" element={<ModelSelectPage />} />
        <Route path="/turbo" element={<TurboPage />} />
        <Route path="/multilingual" element={<MultilingualPage />} />
      </Routes>
    </div>
  );
}