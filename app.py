"""
YouTube Summarizer API - Backend Application
-----------------------------------------
Cette application Flask fournit une API pour résumer et analyser des vidéos YouTube.
Elle utilise l'API OpenAI GPT-4 pour générer des résumés intelligents et d'autres analyses.

Fonctionnalités principales :
- Résumé de vidéos YouTube
- Navigation horodatée avec moments clés
- Transcription améliorée
- Analyse des commentaires

Auteur: Aymen Messaoudi
Date: Avril 2025
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from openai import OpenAI
from functools import lru_cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import re
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Initialisation de l'application
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration du rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per minute"],
    enabled=not app.config.get('TESTING', False)  # Désactive le rate limiting en mode test
)

# Configuration
PORT = int(os.getenv("PORT", 5000))
MAX_CHARS = 12000
YOUTUBE_ID_REGEX = r'^[a-zA-Z0-9_-]{11}$'
SUPPORTED_LANGUAGES = ['fr', 'en']

# Client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def validate_video_id(video_id: str) -> bool:
    """Valide le format de l'ID vidéo YouTube."""
    return bool(re.match(YOUTUBE_ID_REGEX, video_id))

def validate_language(lang: str) -> str:
    """Valide et retourne la langue supportée."""
    lang = lang.lower()
    return lang if lang in SUPPORTED_LANGUAGES else 'fr'

@lru_cache(maxsize=100)
def get_transcript(video_id: str, target_lang: str = 'fr') -> Tuple[Optional[List[Dict]], str, int]:
    """
    Récupère la transcription d'une vidéo YouTube avec mise en cache.
    
    Args:
        video_id (str): L'identifiant de la vidéo YouTube
        target_lang (str): La langue cible pour la transcription
    
    Returns:
        Tuple[Optional[List[Dict]], str, int]: (transcription, message d'erreur, code HTTP)
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return transcript_list, "", 200
    except NoTranscriptFound:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[target_lang])
            return transcript_list, "", 200
        except NoTranscriptFound:
            logger.error(f"Transcription non trouvée pour {video_id}")
            return None, f"Aucun sous-titre disponible dans les langues spécifiées ({target_lang})", 404
        except TranscriptsDisabled:
            logger.warning(f"Transcription désactivée pour la vidéo {video_id}")
            return None, "Transcription désactivée pour cette vidéo", 403
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la transcription: {str(e)}")
            return None, str(e), 500
    except TranscriptsDisabled:
        logger.warning(f"Transcription désactivée pour la vidéo {video_id}")
        return None, "Transcription désactivée pour cette vidéo", 403
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la transcription: {str(e)}")
        return None, str(e), 500

def truncate_text(text: str, max_chars: int = MAX_CHARS) -> str:
    """Tronque le texte à la limite spécifiée."""
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[Tronqué à cause de la taille maximale]"
    return text

def create_error_response(message: str, status_code: int) -> Tuple[Dict, int]:
    """Crée une réponse d'erreur standardisée."""
    return jsonify({
        "error": {
            "message": message,
            "status": status_code
        }
    }), status_code

@app.errorhandler(429)
def ratelimit_handler(e):
    """Gestionnaire pour les erreurs de rate limiting."""
    return create_error_response(
        "Trop de requêtes. Veuillez réessayer plus tard.",
        429
    )

# Routes API

@app.route('/api/summarize', methods=['POST'])
@limiter.limit("5 per minute")
def summarize():
    """Route principale pour résumer une vidéo YouTube."""
    try:
        data = request.get_json()
        if not data:
            return create_error_response("Corps de requête JSON requis", 400)

        video_id = data.get("videoId")
        if not video_id:
            return create_error_response("videoId est requis", 400)
        
        if not validate_video_id(video_id):
            return create_error_response("Format d'ID vidéo YouTube invalide", 400)

        target_lang = validate_language(data.get("targetLang", "fr"))
        
        transcript_list, error_message, status_code = get_transcript(video_id, target_lang)
        if error_message:
            return create_error_response(error_message, status_code)

        transcript_text = " ".join([entry["text"] for entry in transcript_list])
        transcript_text = truncate_text(transcript_text)

        prompt = f"""
        Tu es un assistant intelligent. Résume le contenu suivant, qui est une transcription brute d'une vidéo YouTube.

        Ta mission :
        - Résume uniquement en français 🇫🇷
        - Formate en **bullet points clairs** avec des titres en gras
        - Pas d'introduction, pas de conclusion, pas de traduction en anglais
        - Garde uniquement les informations utiles
        - Utilise **le style Markdown** :
          - Exemple :
            - **Sujet :** Contenu
            - **Sujet 2 :** Autre contenu

        Voici la transcription :
        {transcript_text}
        """

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant de résumé vidéo YouTube multilingue."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return jsonify({
            "summary": response.choices[0].message.content,
            "metadata": {
                "videoId": video_id,
                "language": target_lang,
                "charCount": len(transcript_text)
            }
        })

    except Exception as e:
        logger.error(f"Erreur lors du résumé: {str(e)}")
        return create_error_response(f"Erreur lors du traitement: {str(e)}", 500)

@app.route('/api/timestamped-summary', methods=['POST'])
@limiter.limit("5 per minute")
def get_timestamped_summary():
    """Route pour obtenir un résumé chronologique avec les moments importants."""
    try:
        data = request.get_json()
        if not data:
            return create_error_response("Corps de requête JSON requis", 400)

        video_id = data.get("videoId")
        if not video_id:
            return create_error_response("videoId est requis", 400)
        
        if not validate_video_id(video_id):
            return create_error_response("Format d'ID vidéo YouTube invalide", 400)

        target_lang = validate_language(data.get("targetLang", "fr"))
        
        transcript_list, error_message, status_code = get_transcript(video_id, target_lang)
        if error_message:
            return create_error_response(error_message, status_code)

        transcript_text = " ".join([entry["text"] for entry in transcript_list])
        transcript_text = truncate_text(transcript_text)

        timestamps = [
            {"time": entry["start"], 
             "text": entry["text"],
             "duration": entry["duration"]} 
            for entry in transcript_list
        ]

        prompt = f"""
        Analyse cette transcription de vidéo YouTube et identifie les moments clés importants.

        Instructions spécifiques :
        1. Identifie 5-8 moments clés de la vidéo
        2. Pour chaque moment :
           - Donne un titre descriptif concis en français
           - Explique brièvement pourquoi ce moment est important
        3. Formate la sortie en JSON avec la structure suivante :
           {{
             "keyMoments": [
               {{
                 "title": "Titre du moment",
                 "description": "Description courte",
                 "importance": "Pourquoi ce moment est important"
               }}
             ]
           }}

        Transcription :
        {transcript_text}
        """

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse vidéo qui identifie les moments clés."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return jsonify({
            "analysis": response.choices[0].message.content,
            "timestamps": timestamps,
            "metadata": {
                "videoId": video_id,
                "language": target_lang,
                "momentsCount": len(timestamps)
            }
        })

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse chronologique: {str(e)}")
        return create_error_response(f"Erreur lors du traitement: {str(e)}", 500)

@app.route('/api/enhanced-transcript', methods=['POST'])
@limiter.limit("5 per minute")
def get_enhanced_transcript():
    """Route pour obtenir une version améliorée de la transcription."""
    try:
        data = request.get_json()
        if not data:
            return create_error_response("Corps de requête JSON requis", 400)

        video_id = data.get("videoId")
        if not video_id:
            return create_error_response("videoId est requis", 400)
        
        if not validate_video_id(video_id):
            return create_error_response("Format d'ID vidéo YouTube invalide", 400)

        target_lang = validate_language(data.get("targetLang", "fr"))
        
        transcript_list, error_message, status_code = get_transcript(video_id, target_lang)
        if error_message:
            return create_error_response(error_message, status_code)

        transcript_text = " ".join([entry["text"] for entry in transcript_list])
        transcript_text = truncate_text(transcript_text)

        prompt = f"""
        Améliore cette transcription brute de vidéo YouTube pour la rendre plus lisible et professionnelle.

        Instructions spécifiques :
        1. Corrige la grammaire et la ponctuation en français
        2. Organise le texte en paragraphes logiques
        3. Ajoute des marqueurs de structure (introduction, développement, conclusion)
        4. Conserve le sens original mais améliore la clarté
        5. Formate la sortie en JSON avec cette structure :
           {{
             "enhancedTranscript": "Le texte amélioré",
             "sections": ["Liste des sections principales"],
             "readabilityScore": "Score de lisibilité sur 10"
           }}

        Transcription originale :
        {transcript_text}
        """

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en rédaction qui améliore la qualité des transcriptions."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return jsonify({
            "result": response.choices[0].message.content,
            "metadata": {
                "videoId": video_id,
                "language": target_lang,
                "originalLength": len(transcript_text)
            }
        })

    except Exception as e:
        logger.error(f"Erreur lors de l'amélioration de la transcription: {str(e)}")
        return create_error_response(f"Erreur lors du traitement: {str(e)}", 500)

@app.route('/api/top-comments', methods=['POST'])
@limiter.limit("5 per minute")
def analyze_comments():
    """Route pour analyser et générer des commentaires pertinents."""
    try:
        data = request.get_json()
        if not data:
            return create_error_response("Corps de requête JSON requis", 400)

        video_id = data.get("videoId")
        if not video_id:
            return create_error_response("videoId est requis", 400)
        
        if not validate_video_id(video_id):
            return create_error_response("Format d'ID vidéo YouTube invalide", 400)

        target_lang = validate_language(data.get("targetLang", "fr"))
        
        transcript_list, error_message, status_code = get_transcript(video_id, target_lang)
        if error_message:
            return create_error_response(error_message, status_code)

        transcript_text = " ".join([entry["text"] for entry in transcript_list])
        transcript_text = truncate_text(transcript_text)

        prompt = f"""
        En te basant sur le contenu de cette vidéo, génère et analyse des commentaires pertinents.

        Instructions spécifiques :
        1. Génère 5 commentaires réalistes qui pourraient apparaître sous cette vidéo, en français
        2. Pour chaque commentaire :
           - Crée un nom d'utilisateur réaliste
           - Ajoute un nombre de likes plausible
           - Évalue sa pertinence
        3. Formate la sortie en JSON avec cette structure :
           {{
             "topComments": [
               {{
                 "username": "nom_utilisateur",
                 "comment": "texte du commentaire",
                 "likes": nombre_de_likes,
                 "relevance": "score de pertinence sur 10"
               }}
             ],
             "analysisInsights": "aperçu global des réactions"
           }}

        Contenu de la vidéo :
        {transcript_text}
        """

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse de contenu social qui comprend les dynamiques des commentaires YouTube."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return jsonify({
            "result": response.choices[0].message.content,
            "metadata": {
                "videoId": video_id,
                "language": target_lang,
                "generatedAt": datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des commentaires: {str(e)}")
        return create_error_response(f"Erreur lors du traitement: {str(e)}", 500)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Route de vérification de l'état de l'API."""
    return jsonify({
        "status": "healthy",
        "version": "1.1.0",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Vérification de la configuration
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("La clé API OpenAI n'est pas configurée!")
        exit(1)

    # Démarrage du serveur
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv("FLASK_ENV") == "development")
