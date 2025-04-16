# Guide d'intégration Frontend - YouTube Summarizer API

Ce guide détaille l'intégration de l'API YouTube Summarizer dans votre application frontend.

## Configuration de base

1. URL de base de l'API :
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

2. Headers requis pour les requêtes :
```javascript
const headers = {
  'Content-Type': 'application/json'
};
```

## Validation des entrées

```javascript
// Validation de l'ID YouTube
function isValidYouTubeId(id) {
  return /^[a-zA-Z0-9_-]{11}$/.test(id);
}

// Validation de la langue
function isValidLanguage(lang) {
  return ['fr', 'en'].includes(lang.toLowerCase());
}
```

## Gestion du Rate Limiting

```javascript
class RateLimitError extends Error {
  constructor(message = 'Trop de requêtes, veuillez réessayer plus tard.') {
    super(message);
    this.name = 'RateLimitError';
  }
}

async function handleRateLimit(response) {
  if (response.status === 429) {
    throw new RateLimitError();
  }
  return response;
}
```

## Exemples d'utilisation avec fetch

### 1. Résumé de vidéo
```javascript
async function getSummary(videoId, targetLang = 'fr') {
  try {
    if (!isValidYouTubeId(videoId)) {
      throw new Error('ID YouTube invalide');
    }

    const response = await fetch(`${API_BASE_URL}/summarize`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ videoId, targetLang })
    });
    
    await handleRateLimit(response);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error?.message || 'Une erreur est survenue');
    }
    
    return {
      summary: data.summary,
      metadata: data.metadata // Nouvelles métadonnées incluses
    };
  } catch (error) {
    console.error('Erreur lors de la récupération du résumé:', error);
    throw error;
  }
}
```

### 2. Navigation horodatée
```javascript
async function getTimestampedSummary(videoId, targetLang = 'fr') {
  try {
    if (!isValidYouTubeId(videoId)) {
      throw new Error('ID YouTube invalide');
    }

    const response = await fetch(`${API_BASE_URL}/timestamped-summary`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ videoId, targetLang })
    });
    
    await handleRateLimit(response);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error?.message || 'Une erreur est survenue');
    }
    
    return {
      keyMoments: data.analysis.keyMoments,
      timestamps: data.timestamps
    };
  } catch (error) {
    console.error('Erreur lors de la récupération des moments clés:', error);
    throw error;
  }
}
```

### 3. Transcription améliorée
```javascript
async function getEnhancedTranscript(videoId, targetLang = 'fr') {
  try {
    if (!isValidYouTubeId(videoId)) {
      throw new Error('ID YouTube invalide');
    }

    const response = await fetch(`${API_BASE_URL}/enhanced-transcript`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ videoId, targetLang })
    });
    
    await handleRateLimit(response);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error?.message || 'Une erreur est survenue');
    }
    
    return data.result;
  } catch (error) {
    console.error('Erreur lors de la récupération de la transcription:', error);
    throw error;
  }
}
```

### 4. Analyse des commentaires
```javascript
async function getTopComments(videoId) {
  try {
    if (!isValidYouTubeId(videoId)) {
      throw new Error('ID YouTube invalide');
    }

    const response = await fetch(`${API_BASE_URL}/top-comments`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ videoId })
    });
    
    await handleRateLimit(response);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error?.message || 'Une erreur est survenue');
    }
    
    return data.result;
  } catch (error) {
    console.error('Erreur lors de la récupération des commentaires:', error);
    throw error;
  }
}
```

### 5. Vérification de l'état de l'API
```javascript
async function checkApiHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    
    return {
      isHealthy: data.status === 'healthy',
      version: data.version,
      timestamp: new Date(data.timestamp)
    };
  } catch (error) {
    console.error('Erreur lors de la vérification de l\'état de l\'API:', error);
    return { isHealthy: false };
  }
}
```

## Gestion des erreurs

L'API retourne des erreurs standardisées :

```typescript
interface ApiError {
  error: {
    message: string;
    status: number;
  };
}
```

Codes d'erreur HTTP :
- **400** : Requête invalide (videoId manquant ou invalide)
- **404** : Sous-titres non disponibles
- **403** : Transcription désactivée pour la vidéo
- **429** : Rate limit dépassé
- **500** : Erreur serveur

## Exemples de réponses JSON

### 1. Résumé (/api/summarize)
```json
{
  "summary": "- **Introduction** : Présentation du sujet\n- **Point clé 1** : Description...\n...",
  "metadata": {
    "videoId": "dQw4w9WgXcQ",
    "language": "fr",
    "charCount": 5432
  }
}
```

### 2. Navigation horodatée (/api/timestamped-summary)
```json
{
  "analysis": {
    "keyMoments": [
      {
        "title": "Introduction au sujet",
        "description": "Le présentateur expose les concepts clés",
        "importance": "Établit le contexte de la vidéo"
      }
    ]
  },
  "timestamps": [
    {
      "time": 0.0,
      "text": "Bonjour à tous",
      "duration": 2.5
    }
  ]
}
```

### 3. Transcription améliorée (/api/enhanced-transcript)
```json
{
  "result": {
    "enhancedTranscript": "Texte amélioré et formaté...",
    "sections": ["Introduction", "Développement", "Conclusion"],
    "readabilityScore": "8/10"
  }
}
```

### 4. Analyse des commentaires (/api/top-comments)
```json
{
  "result": {
    "topComments": [
      {
        "username": "TechExpert",
        "comment": "Excellente explication !",
        "likes": 1234,
        "relevance": "9/10"
      }
    ],
    "analysisInsights": "Les commentaires sont majoritairement positifs..."
  }
}
```

### 5. État de l'API (/api/health)
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "timestamp": "2025-04-16T14:30:00Z"
}
```

## Bonnes pratiques d'intégration

### 1. Gestion du cache côté client
```javascript
const cache = new Map();

function getCachedResult(key) {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < 3600000) { // 1 heure
    return cached.data;
  }
  return null;
}

function setCachedResult(key, value) {
  cache.set(key, {
    data: value,
    timestamp: Date.now()
  });
}
```

### 2. Extraction de l'ID YouTube
```javascript
function extractVideoId(url) {
  const regex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
  const match = url.match(regex);
  return match ? match[1] : null;
}
```

### 3. Gestion des états d'interface
```javascript
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState(null);
const [data, setData] = useState(null);

// Exemple d'utilisation
async function fetchVideoSummary(videoId) {
  setIsLoading(true);
  setError(null);
  try {
    // Vérifier le cache d'abord
    const cached = getCachedResult(`summary-${videoId}`);
    if (cached) {
      setData(cached);
      return;
    }
    
    const result = await getSummary(videoId);
    setCachedResult(`summary-${videoId}`, result);
    setData(result);
  } catch (error) {
    setError(error.message);
  } finally {
    setIsLoading(false);
  }
}
```