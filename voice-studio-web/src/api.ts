import axios from "axios";

export const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

export async function synthesize(params: {
    text: string;
    language: string;
    force_model: "chatterbox_turbo" | "chatterbox_multilingual";
    emotion?: string;
    speaker_wav?: File | null;
}) {
    const form = new FormData();
    form.append("text", params.text);
    form.append("language", params.language);
    form.append("force_model", params.force_model);
    if (params.emotion) form.append("emotion", params.emotion);
    if (params.speaker_wav) form.append("speaker_wav", params.speaker_wav);

    const { data } = await api.post("/synthesize", form, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
}

export async function translateWithGemini(input: {
    text: string;
    target_language: string;
}) {
    const { data } = await api.post("/translate", input);
    return data as { translated_text: string };
}