import { Link } from "react-router-dom";

export default function ModelSelectPage() {
  return (
    <div>
      <div className="page-header">
        <span className="page-header__icon">🧠</span>
        <h1>Choose Your Engine</h1>
        <p>Select a voice synthesis model to start generating speech</p>
      </div>

      <div className="hero__cards">
        <Link to="/turbo" style={{ textDecoration: "none" }}>
          <div className="card">
            <span className="card__icon">⚡</span>
            <h2>Turbo</h2>
            <p>
              High-fidelity English voice cloning with emotion control and
              reference audio. Ultra-fast inference.
            </p>
            <span className="btn btn--outline">Open Turbo →</span>
          </div>
        </Link>

        <Link to="/multilingual" style={{ textDecoration: "none" }}>
          <div className="card">
            <span className="card__icon">🌍</span>
            <h2>Multilingual</h2>
            <p>
              Generate speech in 23+ languages with automatic Gemini translation
              and voice cloning.
            </p>
            <span className="btn btn--outline">Open Multilingual →</span>
          </div>
        </Link>
      </div>
    </div>
  );
}