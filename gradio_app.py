import os
import gradio as gr
from dotenv import load_dotenv

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_elevenlabs

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# System prompt for AI doctor response
SYSTEM_PROMPT = (
    "You are a professional doctor. Analyze the image for any medical issues. "
    "Provide possible differentials and suggest remedies concisely (max 2 sentences). "
    "Avoid numbers, special characters, markdown, or AI disclaimers. "
    "Speak as if addressing a real patient. Example: 'With what I see, I think you have...' "
)

def process_inputs(audio_filepath, image_filepath):
    """Processes audio and image inputs to generate a medical response."""
    
    # Transcribe audio
    speech_text = transcribe_with_groq(GROQ_API_KEY, audio_filepath, stt_model="whisper-large-v3")

    # Generate doctor response based on image analysis
    if image_filepath:
        encoded_image = encode_image(image_filepath)
        query = f"{SYSTEM_PROMPT} {speech_text}"
        doctor_response = analyze_image_with_query(query=query, encoded_image=encoded_image, model="llama-3.2-11b-vision-preview")
    else:
        doctor_response = "No image provided for analysis."

    # Convert doctor's response to speech
    voice_response = text_to_speech_with_elevenlabs(input_text=doctor_response, output_filepath="final.mp3")

    return speech_text, doctor_response, voice_response

# Gradio interface
iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath"),
        gr.Image(type="filepath")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio("final.mp3")
    ],
    title="AI Doctor with Vision and Voice"
)

if __name__ == "__main__":
    iface.launch(debug=True)
