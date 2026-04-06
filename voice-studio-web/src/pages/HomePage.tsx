import { Link } from "react-router-dom";

export default function HomePage() {
    return (
        <div className="card">
            <h1>Voice Studio</h1>
            <p>Generate speech with Chatterbox Turbo and Multilingual models.</p>
            <Link className="btn" to="/models">Go to Model Selection</Link>
        </div>
    );
}