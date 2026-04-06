import { useState } from "react";
import { synthesize } from "../api";
import AudioResult from "../components/AudioResult";

export default function TurboPage() {
    const [text, setText] = useState("Hi, this is a turbo test.");
    const [emotion, setEmotion] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [audioPath, setAudioPath] = useState("");
    const [loading, setLoading] = useState(false);
    const toPublicAudioUrl = (outputPath: string) => {
        const normalized = outputPath.replace(/\\/g, "/");
        const filename = normalized.split("/").pop();
        return `http://127.0.0.1:8000/outputs/${filename}`;
    };

    const onGenerate = async () => {
        setLoading(true);
        try {
            const res = await synthesize({
                text,
                language: "en",
                force_model: "chatterbox_turbo",
                emotion,
                speaker_wav: file,
            });
            setAudioPath(toPublicAudioUrl(res.output_wav_path));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <h2>Turbo</h2>
            <textarea value={text} onChange={(e) => setText(e.target.value)} rows={6} />
            <input value={emotion} onChange={(e) => setEmotion(e.target.value)} placeholder="Emotion (optional)" />
            <input type="file" accept="audio/*" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            <button className="btn" onClick={onGenerate} disabled={loading}>
                {loading ? "Generating..." : "Generate"}
            </button>

            <AudioResult audioUrl={audioPath} />
        </div>
    );
}