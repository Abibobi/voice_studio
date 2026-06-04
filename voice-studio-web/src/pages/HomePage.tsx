import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function HomePage() {
  const { isLoggedIn } = useAuth();

  return (
    <>
      {/* ── Hero Section ── */}
      <section className="hero" id="hero">
        <span className="hero__badge">AI-Powered Voice Engine</span>

        <h1 className="hero__title">
          Clone Any Voice,
          <br />
          In <span>Any Language</span>
        </h1>

        <p className="hero__subtitle">
          Generate natural speech with advanced voice cloning. Use Turbo for
          expressive English or Multilingual for 23+ languages — all powered by
          Chatterbox.
        </p>

        <div className="hero__actions">
          {isLoggedIn ? (
            <Link to="/models" className="btn btn--lg">
              ⚡ Open Studio
            </Link>
          ) : (
            <>
              <Link to="/signup" className="btn btn--lg">
                Get Started — Free
              </Link>
              <Link to="/login" className="btn btn--outline btn--lg">
                Sign In
              </Link>
            </>
          )}
        </div>
      </section>

      {/* ── Feature Cards ── */}
      <section className="features" id="features">
        <div className="features__grid">
          <div className="feature-card">
            <span className="feature-card__icon">⚡</span>
            <h3>Turbo Engine</h3>
            <p>
              High-fidelity English voice cloning with emotion control and
              reference audio. Ultra-fast inference.
            </p>
          </div>

          <div className="feature-card">
            <span className="feature-card__icon">🌍</span>
            <h3>23+ Languages</h3>
            <p>
              Automatic translation via Gemini AI and multilingual speech
              generation from a single English prompt.
            </p>
          </div>

          <div className="feature-card">
            <span className="feature-card__icon">🎤</span>
            <h3>Voice Profiles</h3>
            <p>
              Save and manage voice samples in your personal library. Reuse them
              across sessions instantly.
            </p>
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section className="how-it-works" id="how-it-works">
        <h2 className="section-title">How It Works</h2>
        <div className="steps">
          <div className="step">
            <span className="step__number">1</span>
            <h4>Upload a Voice</h4>
            <p>Record or upload a short voice sample as a reference for cloning.</p>
          </div>
          <div className="step">
            <span className="step__number">2</span>
            <h4>Enter Your Script</h4>
            <p>Type or paste the text you want spoken — in any language.</p>
          </div>
          <div className="step">
            <span className="step__number">3</span>
            <h4>Generate & Download</h4>
            <p>Our AI synthesizes the speech. Listen, iterate, and download the WAV.</p>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="footer">
        <p>
          Built with ❤️ using Chatterbox · Voice Studio © {new Date().getFullYear()}
        </p>
      </footer>
    </>
  );
}