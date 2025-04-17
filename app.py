from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from openai import OpenAI
import os

load_dotenv()

app = Flask(__name__)
from flask_cors import CORS

CORS(app, resources={r"/api/*": {"origins": "*"}})


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_CHARS = 12000  # Pour rester sous les limites de GPT-4

@app.route('/api/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    video_id = data.get("videoId")
    target_lang = data.get("targetLang", "fr")

    if not video_id:
        return jsonify({"error": "videoId is required"}), 400

    transcript_text = ""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        transcript_text = " ".join([entry["text"] for entry in transcript_list])
    except NoTranscriptFound:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[target_lang])
            transcript_text = " ".join([entry["text"] for entry in transcript_list])
        except Exception as fallback_err:
            return jsonify({
                "summary": f"[Erreur : aucun sous-titre disponible dans les langues spécifiées. Vérifie que la vidéo contient des sous-titres auto dans la langue '{target_lang}'.]"
            }), 200
    except TranscriptsDisabled:
        return jsonify({"summary": "[Transcription désactivée pour cette vidéo]"}), 200
    except Exception as e:
        return jsonify({"summary": f"[Erreur technique lors de l’extraction : {str(e)}]"}), 500

    # ✂️ Limite de taille
    if len(transcript_text) > MAX_CHARS:
        transcript_text = transcript_text[:MAX_CHARS]
        transcript_text += "\n\n[Tronqué à cause de la taille maximale]"

    # 💬 Prompt renforcé : résumé en bullet points, français uniquement
    prompt = f"""
    Tu es un assistant intelligent. Résume le contenu suivant, qui est une transcription brute d'une vidéo YouTube.

    Ta mission :
    - Résume uniquement en français 🇫🇷
    - Formate en bullet points clairs avec des titres
    - Pas d’introduction, pas de conclusion, pas de traduction en anglais
    - Garde uniquement les informations utiles
    - Utilise le style Markdown :
      - Exemple :
        - Sujet : Contenu
        - Sujet 2 : Autre contenu

    Voici la transcription :
    {transcript_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # ✅ Utilisation du modèle optimisé
            messages=[
                {"role": "system", "content": "Tu es un assistant de résumé vidéo YouTube multilingue."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.choices[0].message.content
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": f"Erreur OpenAI: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
