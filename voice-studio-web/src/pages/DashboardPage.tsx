import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { listVoiceProfiles, createVoiceProfile, deleteVoiceProfile } from "../api";

type VoiceProfile = {
  id: number;
  name: string;
  language: string;
  sample_wav_path: string;
  created_at: string;
};

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [profiles, setProfiles] = useState<VoiceProfile[]>([]);
  const [name, setName] = useState("");
  const [language, setLanguage] = useState("en");
  const [file, setFile] = useState<File | null>(null);
  const [creating, setCreating] = useState(false);
  const [loadingProfiles, setLoadingProfiles] = useState(true);

  const loadProfiles = async () => {
    try {
      const p = await listVoiceProfiles();
      setProfiles(p);
    } catch {
      /* token might be invalid — ignore */
    } finally {
      setLoadingProfiles(false);
    }
  };

  useEffect(() => {
    loadProfiles();
  }, []);

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !name.trim()) return;
    setCreating(true);
    try {
      await createVoiceProfile({ name, language, sample_wav: file });
      setName("");
      setLanguage("en");
      setFile(null);
      await loadProfiles();
    } catch {
      /* handle silently for now */
    } finally {
      setCreating(false);
    }
  };

  const onDelete = async (id: number) => {
    await deleteVoiceProfile(id);
    await loadProfiles();
  };

  return (
    <div className="dashboard">
      {/* ── Welcome Header ── */}
      <div className="dashboard__header">
        <div>
          <h1>Welcome back 👋</h1>
          <p className="dashboard__email">{user?.email}</p>
        </div>
        <button className="btn btn--outline" onClick={logout}>
          Logout
        </button>
      </div>

      {/* ── Quick Actions ── */}
      <section className="dashboard__actions">
        <Link to="/turbo" className="action-card">
          <span className="action-card__icon">⚡</span>
          <div>
            <h3>Turbo Engine</h3>
            <p>English voice cloning with emotion</p>
          </div>
          <span className="action-card__arrow">→</span>
        </Link>

        <Link to="/multilingual" className="action-card">
          <span className="action-card__icon">🌍</span>
          <div>
            <h3>Multilingual Engine</h3>
            <p>23+ languages with translation</p>
          </div>
          <span className="action-card__arrow">→</span>
        </Link>
      </section>

      {/* ── Voice Profiles ── */}
      <section className="dashboard__profiles">
        <h2>Voice Profiles</h2>

        <form onSubmit={onCreate} className="profile-form card">
          <h3>➕ Create New Profile</h3>
          <div className="profile-form__fields">
            <input
              placeholder="Profile name (e.g. My Narration Voice)"
              value={name}
              onChange={(e) => setName(e.target.value)}
              type="text"
            />
            <input
              placeholder="Language code (en, fr, de…)"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              type="text"
            />
            <label className="file-upload-label file-upload-label--compact">
              <span>🎤 {file ? file.name : "Upload voice sample"}</span>
              <input
                type="file"
                accept="audio/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
            </label>
          </div>
          <button className="btn" type="submit" disabled={creating || !name.trim() || !file}>
            {creating ? (
              <>
                <span className="spinner" /> Saving…
              </>
            ) : (
              "Save Profile"
            )}
          </button>
        </form>

        {loadingProfiles ? (
          <div className="auth-loading">
            <span className="spinner spinner--lg" />
            <p>Loading profiles…</p>
          </div>
        ) : profiles.length === 0 ? (
          <div className="empty-state">
            <span className="empty-state__icon">🎙️</span>
            <h3>No voice profiles yet</h3>
            <p>Create your first voice profile above to get started.</p>
          </div>
        ) : (
          <div className="profiles-grid">
            {profiles.map((p) => (
              <div key={p.id} className="profile-card card">
                <div className="profile-card__info">
                  <h4>{p.name}</h4>
                  <span className="profile-card__lang">{p.language.toUpperCase()}</span>
                </div>
                <p className="profile-card__date">
                  Created {new Date(p.created_at).toLocaleDateString()}
                </p>
                <button
                  className="btn btn--outline btn--sm btn--danger"
                  onClick={() => onDelete(p.id)}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}