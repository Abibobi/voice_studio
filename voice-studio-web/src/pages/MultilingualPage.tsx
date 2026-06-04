import { useState } from "react";
import { Link } from "react-router-dom";
import { synthesize, translateWithGemini } from "../api";
import AudioResult from "../components/AudioResult";
import VoiceSourcePicker from "../components/VoiceSourcePicker";

const LANG_OPTIONS = [
  { code: "en", label: "🇬🇧 English" },
  { code: "fr", label: "🇫🇷 French" },
  { code: "de", label: "🇩🇪 German" },
  { code: "es", label: "🇪🇸 Spanish" },
  { code: "it", label: "🇮🇹 Italian" },
  { code: "pt", label: "🇵🇹 Portuguese" },
  { code: "ja", label: "🇯🇵 Japanese" },
  { code: "ko", label: "🇰🇷 Korean" },
  { code: "hi", label: "🇮🇳 Hindi" },
  { code: "ar", label: "🇸🇦 Arabic" },
  { code: "zh", label: "🇨🇳 Chinese" },
  { code: "ru", label: "🇷🇺 Russian" },
  { code: "nl", label: "🇳🇱 Dutch" },
  { code: "sv", label: "🇸🇪 Swedish" },
  { code: "pl", label: "🇵🇱 Polish" },
  { code: "tr", label: "🇹🇷 Turkish" },
  { code: "da", label: "🇩🇰 Danish" },
  { code: "fi", label: "🇫🇮 Finnish" },
  { code: "no", label: "🇳🇴 Norwegian" },
  { code: "el", label: "🇬🇷 Greek" },
  { code: "he", label: "🇮🇱 Hebrew" },
  { code: "ms", label: "🇲🇾 Malay" },
  { code: "sw", label: "🇰🇪 Swahili" },
];

export default function MultilingualPage() {
  const [text, setText] = useState("Hello! Welcome to Voice Studio.");
  const [language, setLanguage] = useState("fr");
  const [emotion, setEmotion] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [profileId, setProfileId] = useState<number | null>(null);
  const [audioUrl, setAudioUrl] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const toPublicAudioUrl = (outputPath: string) => {
    const normalized = outputPath.replace(/\\/g, "/");
    const filename = normalized.split("/").pop();
    return `http://127.0.0.1:8000/outputs/${filename}`;
  };

  const onGenerate = async () => {
    setLoading(true);
    setError("");
    setTranslatedText("");
    try {
      let finalText = text;
      if (language !== "en") {
        const tr = await translateWithGemini({
          text,
          target_language: language,
        });
        finalText = tr.translated_text;
        setTranslatedText(finalText);
      }

      const res = await synthesize({
        text: finalText,
        language,
        force_model: "chatterbox_multilingual",
        emotion: emotion || undefined,
        speaker_wav: file,
        voice_profile_id: profileId,
      });

      setAudioUrl(toPublicAudioUrl(res.output_wav_path));
    } catch (err: any) {
      setError(
        err?.response?.data?.detail || err?.message || "Generation failed"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Link to="/models" className="breadcrumb">← Back to Models</Link>
      <div className="page-header">
        <span className="page-header__icon">🌍</span>
        <h1>Multilingual Engine</h1>
        <p>
          Generate speech in 23+ languages with automatic Gemini translation and
          voice cloning
        </p>
      </div>

      <div className="card">
        <div className="form-group">
          <label className="form-label">Script (English is fine — it will be translated)</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={5}
            placeholder="Enter your text here..."
          />
        </div>

        <div className="grid" style={{ marginBottom: 18 }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Target Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {LANG_OPTIONS.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Emotion (optional)</label>
            <input
              type="text"
              value={emotion}
              onChange={(e) => setEmotion(e.target.value)}
              placeholder="e.g. happy, calm"
            />
          </div>
        </div>

        <div className="form-group">
          <VoiceSourcePicker
            selectedProfileId={profileId}
            onSelect={setProfileId}
            onUploadFile={setFile}
            uploadedFile={file}
          />
        </div>

        <button
          className="btn btn--full"
          onClick={onGenerate}
          disabled={loading || !text.trim()}
        >
          {loading ? (
            <>
              <span className="spinner" /> Generating...
            </>
          ) : (
            "🌍 Translate + Generate"
          )}
        </button>

        {error && <div className="error-toast">⚠️ {error}</div>}

        {translatedText && (
          <div className="translated-script">
            <h3>📝 Translated Script</h3>
            <p>{translatedText}</p>
          </div>
        )}

        <AudioResult audioUrl={audioUrl} />
      </div>
    </div>
  );
}