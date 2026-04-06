import gradio as gr
import requests

API_BASE = "http://127.0.0.1:8000"

LANGS = ["ar","da","de","el","en","es","fi","fr","he","hi","it","ja","ko","ms","nl","no","pl","pt","ru","sv","sw","tr","zh"]


def run_tts(model_name, text, language, emotion, speaker_wav_path):
    data = {
        "text": text,
        "language": language,
        "force_model": model_name,
    }
    if emotion and emotion.strip():
        data["emotion"] = emotion.strip()

    files = {}
    if speaker_wav_path:
        files["speaker_wav"] = open(speaker_wav_path, "rb")

    try:
        r = requests.post(f"{API_BASE}/synthesize", data=data, files=files or None, timeout=300)
        r.raise_for_status()
        j = r.json()
        return j["output_wav_path"], j
    finally:
        if "speaker_wav" in files:
            files["speaker_wav"].close()


with gr.Blocks(title="Voice Studio") as demo:
    gr.Markdown("# 🎙️ Voice Studio")
    gr.Markdown("Minimal UI for Chatterbox Multilingual and Turbo")

    model_name = gr.Dropdown(
        choices=["chatterbox_multilingual", "chatterbox_turbo"],
        value="chatterbox_multilingual",
        label="Model"
    )

    text = gr.Textbox(
        label="Text",
        lines=4,
        value="Bonjour, je suis tres heureux de vous rencontrer."
    )

    language = gr.Dropdown(choices=LANGS, value="fr", label="Language")
    emotion = gr.Textbox(label="Emotion (optional)", value="")

    speaker_wav = gr.Audio(
        sources=["upload", "microphone"],
        type="filepath",
        label="Reference Audio (optional)"
    )

    run_btn = gr.Button("Generate", variant="primary")

    out_audio = gr.Audio(label="Generated Audio")
    out_json = gr.JSON(label="Response")

    run_btn.click(
        fn=run_tts,
        inputs=[model_name, text, language, emotion, speaker_wav],
        outputs=[out_audio, out_json]
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)