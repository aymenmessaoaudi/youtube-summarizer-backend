# YouTube Summarizer API

API Flask qui utilise l'IA (GPT-4-turbo) pour analyser et résumer des vidéos YouTube. Cette API fournit des fonctionnalités avancées de traitement de contenu vidéo.

## Fonctionnalités

- **Résumé automatique** : Génération de résumés concis et structurés
- **Navigation horodatée** : Identification des moments clés
- **Amélioration de transcription** : Optimisation de la lisibilité
- **Analyse de commentaires** : Extraction des retours pertinents

## Nouvelles fonctionnalités (Avril 2025)

- **Rate Limiting** : Protection contre la surcharge (100 requêtes/jour, 10/minute)
- **Système de cache** : Mise en cache des transcriptions pour de meilleures performances
- **Validation améliorée** : Vérification stricte des IDs YouTube et des langues
- **Monitoring** : Nouvelle route `/api/health` pour surveiller l'état de l'API
- **Métadonnées enrichies** : Informations supplémentaires dans les réponses API

## Prérequis techniques

- Python 3.8+
- Flask et dépendances associées
- Clé API OpenAI
- Accès à l'API YouTube Data (optionnel, pour les futures versions)

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/aymenmessaoaudi/youtube-summarizer-backend.git
cd youtube-summarizer-backend
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Modifier le fichier .env avec vos clés
OPENAI_API_KEY=votre-clé-api
YT_API_KEY=votre-clé-youtube-api
PORT=5000
```

## Structure du projet

```
youtube-summarizer-backend/
│
├── app.py                    # Application Flask principale
├── requirements.txt          # Dépendances Python
├── .env.example             # Exemple de configuration
├── README.md                # Documentation technique
└── FRONTEND_INTEGRATION.md   # Guide d'intégration frontend
```

## API Endpoints

Tous les endpoints acceptent des requêtes POST avec un corps JSON.

### Format général des requêtes

```json
{
    "videoId": "string",     # Requis: ID de la vidéo YouTube (11 caractères)
    "targetLang": "string"   # Optionnel: Code langue (défaut: "fr", supporté: "fr", "en")
}
```

### Routes disponibles

- **POST `/api/summarize`** : Génère un résumé de la vidéo
- **POST `/api/timestamped-summary`** : Fournit une analyse chronologique
- **POST `/api/enhanced-transcript`** : Améliore la transcription
- **POST `/api/top-comments`** : Analyse les commentaires
- **GET `/api/health`** : Vérifie l'état de l'API

Pour les détails d'implémentation frontend et les exemples de réponses, consultez [FRONTEND_INTEGRATION.md](FRONTEND_INTEGRATION.md).

## Configuration technique

### Limites et paramètres

- Limite de caractères : 12000 (pour les requêtes GPT-4)
- Langues supportées : fr, en (plus à venir)
- Timeout par défaut : 30 secondes
- Cache : 100 dernières transcriptions
- Rate limiting : 
  - 100 requêtes par jour
  - 10 requêtes par minute

### Gestion des erreurs

L'API utilise les codes HTTP standards et retourne des messages d'erreur structurés :

```json
{
    "error": {
        "message": "Description de l'erreur",
        "status": 400
    }
}
```

Voir la section "Gestion des erreurs" dans FRONTEND_INTEGRATION.md pour plus de détails.

## Sécurité

- CORS configuré pour accepter les requêtes de tout origine en développement
- Protection des clés API via variables d'environnement
- Validation stricte des entrées utilisateur
- Rate limiting pour prévenir les abus
- Validation des IDs YouTube avec regex

## Performance

- Mise en cache des transcriptions (LRU Cache)
- Optimisation des requêtes GPT-4
- Structure JSON optimisée pour les réponses
- Logging pour le débogage et monitoring

## Développement

Pour lancer l'application en mode développement :
```bash
python app.py
```

Le serveur démarre sur le port spécifié dans `.env` (par défaut : 5000)

## Tests

Les tests seront ajoutés dans une prochaine version.

## Prochaines évolutions

- Tests unitaires et d'intégration
- Documentation OpenAPI/Swagger
- Cache distribué (Redis)
- Gestion avancée des erreurs OpenAI
- Support multilingue étendu

## Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## Licence

MIT

## Remerciements

Basé sur [yt-summarizer](https://github.com/doneber/yt-summarizer) de doneber, avec des fonctionnalités étendues.