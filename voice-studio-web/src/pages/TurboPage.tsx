import { useState } from "react";
import { Link } from "react-router-dom";
import { synthesize } from "../api";
import AudioResult from "../components/AudioResult";
import VoiceSourcePicker from "../components/VoiceSourcePicker";

export default function TurboPage() {
  const [text, setText] = useState("Hi, this is a turbo voice cloning test.");
  const [emotion, setEmotion] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [profileId, setProfileId] = useState<number | null>(null);
  const [audioUrl, setAudioUrl] = useState("");
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
    try {
      const res = await synthesize({
        text,
        language: "en",
        force_model: "chatterbox_turbo",
        emotion: emotion || undefined,
        speaker_wav: file,
        voice_profile_id: profileId,
      });
      setAudioUrl(toPublicAudioUrl(res.output_wav_path));
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Link to="/models" className="breadcrumb">← Back to Models</Link>
      <div className="page-header">
        <span className="page-header__icon">⚡</span>
        <h1>Turbo Engine</h1>
        <p>High-fidelity English voice cloning with emotion control</p>
      </div>

      <div className="card">
        <div className="form-group">
          <label className="form-label">Script</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={5}
            placeholder="Enter the text you want to synthesize..."
          />
        </div>

        <div className="form-group">
          <label className="form-label">Emotion (optional)</label>
          <input
            type="text"
            value={emotion}
            onChange={(e) => setEmotion(e.target.value)}
            placeholder="e.g. happy, sad, excited, angry"
          />
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
            "⚡ Generate Speech"
          )}
        </button>

        {error && <div className="error-toast">⚠️ {error}</div>}

        <AudioResult audioUrl={audioUrl} />
      </div>
    </div>
  );
}