"""Voice input (Whisper STT) and output (pyttsx3 TTS)."""

from config import VOICE_RATE, VOICE_LANGUAGE, WHISPER_MODEL


def listen(timeout: int = 8, phrase_limit: int = 30) -> str:
    """
    Record from microphone and transcribe using OpenAI Whisper.
    Returns transcribed text or an error message.
    """
    try:
        import speech_recognition as sr
    except ImportError:
        return "[voice] SpeechRecognition not installed."

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("[Listening... speak now]")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return "[voice] No speech detected."

    try:
        # Use Whisper locally
        import whisper
        import tempfile, os, wave

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp = f.name
        with wave.open(tmp, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.sample_width)
            wf.setframerate(audio.sample_rate)
            wf.writeframes(audio.frame_data)

        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(tmp)
        os.unlink(tmp)
        return result["text"].strip()
    except Exception as e:
        return f"[voice] Transcription error: {e}"


def speak(text: str) -> None:
    """Convert text to speech and play it."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", VOICE_RATE)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS error: {e}] {text}")
