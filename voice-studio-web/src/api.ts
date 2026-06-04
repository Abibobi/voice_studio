import axios from "axios";
import { getToken } from "./lib/auth";

export const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

api.interceptors.request.use((config) => {
    const token = getToken();
    if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export async function signup(email: string, password: string) {
    const { data } = await api.post("/auth/signup", { email, password });
    return data;
}

export async function login(email: string, password: string) {
    const { data } = await api.post("/auth/login", { email, password });
    return data as { access_token: string; token_type: string };
}

export async function me() {
    const { data } = await api.get("/me");
    return data as { id: number; email: string };
}

export async function createVoiceProfile(input: {
    name: string;
    language: string;
    sample_wav: File;
}) {
    const form = new FormData();
    form.append("name", input.name);
    form.append("language", input.language);
    form.append("sample_wav", input.sample_wav);

    const { data } = await api.post("/voice-profiles", form, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
}

export async function listVoiceProfiles() {
    const { data } = await api.get("/voice-profiles");
    return data as Array<{
        id: number;
        name: string;
        language: string;
        sample_wav_path: string;
        created_at: string;
    }>;
}

export async function deleteVoiceProfile(profileId: number) {
    const { data } = await api.delete(`/voice-profiles/${profileId}`);
    return data;
}

export async function synthesize(input: {
    text: string;
    language: string;
    force_model?: string;
    emotion?: string;
    speaker_wav?: File | null;
    voice_profile_id?: number | null;
}) {
    const form = new FormData();
    form.append("text", input.text);
    form.append("language", input.language);
    if (input.force_model) form.append("force_model", input.force_model);
    if (input.emotion) form.append("emotion", input.emotion);
    if (input.voice_profile_id) form.append("voice_profile_id", String(input.voice_profile_id));
    if (input.speaker_wav) form.append("speaker_wav", input.speaker_wav);

    const { data } = await api.post("/synthesize", form, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return data as { output_wav_path: string };
}

export async function translateWithGemini(input: {
    text: string;
    target_language: string;
}) {
    const { data } = await api.post("/translate", input);
    return data as { translated_text: string };
}