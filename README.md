# YouTube Summarizer API

Une API Flask qui utilise l'IA pour générer des résumés de vidéos YouTube, extraire les moments clés avec horodatage, améliorer les transcriptions et analyser les meilleurs commentaires.

## Fonctionnalités

- **Résumés de vidéos** : Génère automatiquement un résumé pour n'importe quelle vidéo YouTube
- **Navigation horodatée** : Identifie les moments clés de la vidéo avec leurs timestamps
- **Aperçu des meilleurs commentaires** : Analyse et met en évidence les commentaires les plus pertinents
- **Générateur de transcription amélioré** : Transforme la transcription brute en texte bien formaté

## Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/aymenmessaoaudi/youtube-summarizer.git
cd youtube-summarizer/youtube-summarizer-backend
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez votre clé API OpenAI :
```bash
# Sur Windows
set OPENAI_API_KEY=votre-clé-api

# Sur Linux/macOS
export OPENAI_API_KEY=votre-clé-api
```

## Utilisation

Lancez l'application :
```bash
python app.py
```

### Endpoints API

- **GET /api/<video_id>** : Obtenir un résumé de la vidéo
- **GET /api/timestamped/<video_id>** : Obtenir les moments clés avec horodatage
- **GET /api/comments/<video_id>** : Obtenir les meilleurs commentaires de la vidéo
- **GET /api/transcript/<video_id>** : Obtenir une transcription améliorée de la vidéo

## Développement futur

Ce projet est en constante évolution. Voici quelques fonctionnalités prévues :

- Analyse de sentiment des vidéos et commentaires
- Filtrage par sujet spécifique
- Support multilingue étendu
- Intégration complète avec l'API YouTube Data

## Licence

MIT

## Remerciements

Ce projet est basé sur [yt-summarizer](https://github.com/doneber/yt-summarizer) de doneber, avec des fonctionnalités étendues.