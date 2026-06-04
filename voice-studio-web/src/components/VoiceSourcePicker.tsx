import { useEffect, useState } from "react";
import { listVoiceProfiles } from "../api";

type VoiceProfile = {
  id: number;
  name: string;
  language: string;
  sample_wav_path: string;
  created_at: string;
};

type Props = {
  selectedProfileId: number | null;
  onSelect: (id: number | null) => void;
  onUploadFile: (file: File | null) => void;
  uploadedFile: File | null;
};

export default function VoiceSourcePicker({
  selectedProfileId,
  onSelect,
  onUploadFile,
  uploadedFile,
}: Props) {
  const [profiles, setProfiles] = useState<VoiceProfile[]>([]);
  const [mode, setMode] = useState<"profile" | "upload">("profile");
  const [loadingProfiles, setLoadingProfiles] = useState(true);

  useEffect(() => {
    listVoiceProfiles()
      .then((p) => setProfiles(p))
      .catch(() => {})
      .finally(() => setLoadingProfiles(false));
  }, []);

  const handleModeSwitch = (newMode: "profile" | "upload") => {
    setMode(newMode);
    if (newMode === "profile") {
      onUploadFile(null);
    } else {
      onSelect(null);
    }
  };

  return (
    <div className="voice-source">
      <label className="form-label">Voice Source</label>

      {/* Toggle */}
      <div className="voice-source__toggle">
        <button
          type="button"
          className={`voice-source__tab ${mode === "profile" ? "voice-source__tab--active" : ""}`}
          onClick={() => handleModeSwitch("profile")}
        >
          📂 Saved Profile
        </button>
        <button
          type="button"
          className={`voice-source__tab ${mode === "upload" ? "voice-source__tab--active" : ""}`}
          onClick={() => handleModeSwitch("upload")}
        >
          📤 Upload New
        </button>
      </div>

      {mode === "profile" ? (
        <div className="voice-source__profiles">
          {loadingProfiles ? (
            <div className="voice-source__loading">
              <span className="spinner" /> Loading profiles…
            </div>
          ) : profiles.length === 0 ? (
            <div className="voice-source__empty">
              <p>No saved profiles. <span onClick={() => handleModeSwitch("upload")} className="auth-link" style={{ cursor: "pointer" }}>Upload a voice</span> or create profiles in your <a href="/dashboard" className="auth-link">Dashboard</a>.</p>
            </div>
          ) : (
            <div className="voice-source__list">
              {profiles.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  className={`voice-source__item ${selectedProfileId === p.id ? "voice-source__item--selected" : ""}`}
                  onClick={() => onSelect(selectedProfileId === p.id ? null : p.id)}
                >
                  <span className="voice-source__item-icon">🎙️</span>
                  <div className="voice-source__item-info">
                    <strong>{p.name}</strong>
                    <span>{p.language.toUpperCase()}</span>
                  </div>
                  {selectedProfileId === p.id && (
                    <span className="voice-source__check">✓</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <label className="file-upload-label">
          <span className="file-upload__icon">🎤</span>
          <span className="file-upload__text">Upload Reference Voice</span>
          <span className="file-upload__hint">
            Upload a sample of the voice you want to clone
          </span>
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => onUploadFile(e.target.files?.[0] || null)}
          />
          {uploadedFile && (
            <span className="file-name">📎 {uploadedFile.name}</span>
          )}
        </label>
      )}
    </div>
  );
}
