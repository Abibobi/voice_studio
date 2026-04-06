import { useState } from "react";
import { synthesize, translateWithGemini } from "../api";
import AudioResult from "../components/AudioResult";

const LANG_OPTIONS = [
    { code: "en", label: "English (en)" },
    { code: "fr", label: "French (fr)" },
    { code: "de", label: "German (de)" },
    { code: "es", label: "Spanish (es)" },
    { code: "it", label: "Italian (it)" },
    { code: "pt", label: "Portuguese (pt)" },
    { code: "ja", label: "Japanese (ja)" },
    { code: "ko", label: "Korean (ko)" },
    { code: "hi", label: "Hindi (hi)" },
    { code: "ar", label: "Arabic (ar)" },
    { code: "zh", label: "Chinese (zh)" },
];

export default function MultilingualPage() {
    const [text, setText] = useState("Hello! Welcome to Voice Studio.");
    const [language, setLanguage] = useState("fr");
    const [emotion, setEmotion] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [audioPath, setAudioPath] = useState("");
    const [translatedText, setTranslatedText] = useState("");
    const [loading, setLoading] = useState(false);

    const toPublicAudioUrl = (outputPath: string) => {
        const normalized = outputPath.replace(/\\/g, "/");
        const filename = normalized.split("/").pop();
        return `http://127.0.0.1:8000/outputs/${filename}`;
    };

    const onGenerate = async () => {
        setLoading(true);
        setTranslatedText("");
        try {
            let finalText = text;
            if (language !== "en") {
                const tr = await translateWithGemini({ text, target_language: language });
                finalText = tr.translated_text;
                setTranslatedText(finalText);
            }

            const res = await synthesize({
                text: finalText,
                language,
                force_model: "chatterbox_multilingual",
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
            <h2>Multilingual</h2>

            <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={6}
                placeholder="Enter your text (English is fine — it will be translated)"
            />

            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                {LANG_OPTIONS.map((l) => (
                    <option key={l.code} value={l.code}>
                        {l.label}
                    </option>
                ))}
            </select>

            <input
                value={emotion}
                onChange={(e) => setEmotion(e.target.value)}
                placeholder="Emotion (optional)"
            />

            <label className="file-upload-label">
                <span>🎤 Upload Reference Voice (for cloning)</span>
                <input
                    type="file"
                    accept="audio/*"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                {file && <span className="file-name">{file.name}</span>}
            </label>

            <button className="btn" onClick={onGenerate} disabled={loading}>
                {loading ? "Generating..." : "Translate + Generate"}
            </button>

            {translatedText && (
                <div className="translated-script">
                    <h3>📝 Translated Script</h3>
                    <p>{translatedText}</p>
                </div>
            )}

            <AudioResult audioUrl={audioPath} />
        </div>
    );
}