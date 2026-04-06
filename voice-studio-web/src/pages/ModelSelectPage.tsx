import { Link } from "react-router-dom";

export default function ModelSelectPage() {
    return (
        <div className="grid">
            <div className="card">
                <h2>Turbo</h2>
                <p>Best for voice similarity cloning with reference audio.</p>
                <Link className="btn" to="/turbo">Open Turbo</Link>
            </div>
            <div className="card">
                <h2>Multilingual</h2>
                <p>Best for non-English generation and language switching.</p>
                <Link className="btn" to="/multilingual">Open Multilingual</Link>
            </div>
        </div>
    );
}