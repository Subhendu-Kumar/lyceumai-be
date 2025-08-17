import os
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()

aai.settings.api_key = os.getenv("ASSEMBLY_AI_API_KEY")

aai_config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)

aai_transcriber = aai.Transcriber(config=aai_config)
