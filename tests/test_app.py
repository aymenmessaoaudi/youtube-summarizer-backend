import pytest
from unittest.mock import patch, MagicMock
from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'healthy'
    assert 'version' in data
    assert 'timestamp' in data

@pytest.mark.parametrize(
    "video_id,target_lang,expected_status",
    [
        ("dQw4w9WgXcQ", "fr", 200),  # Valid video ID
        ("", "fr", 400),  # Empty video ID
        ("invalid_id", "fr", 400),  # Invalid video ID format
        ("dQw4w9WgXcQ", "invalid", 200),  # Invalid language defaults to fr
    ]
)
def test_summarize_validation(client, video_id, target_lang, expected_status, mock_openai, mock_youtube_transcript_api):
    """Test input validation for the summarize endpoint"""
    with patch('app.client', mock_openai), \
         patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript', mock_youtube_transcript_api):
        
        response = client.post('/api/summarize', json={
            "videoId": video_id,
            "targetLang": target_lang
        })
        assert response.status_code == expected_status

def test_summarize_success(client, mock_openai, mock_youtube_transcript_api):
    """Test successful video summarization"""
    with patch('app.client', mock_openai), \
         patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript', mock_youtube_transcript_api):
        
        response = client.post('/api/summarize', json={
            "videoId": "dQw4w9WgXcQ",
            "targetLang": "fr"
        })
        
        assert response.status_code == 200
        data = response.json
        assert 'summary' in data
        assert 'metadata' in data
        assert data['metadata']['videoId'] == "dQw4w9WgXcQ"

def test_summarize_no_transcript(client):
    """Test handling of videos with no available transcript"""
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get_transcript:
        mock_get_transcript.side_effect = NoTranscriptFound('video_id', ['fr'], {})
        
        response = client.post('/api/summarize', json={
            "videoId": "dQw4w9WgXcQ",
            "targetLang": "fr"
        })
        
        assert response.status_code == 404
        assert 'error' in response.json

def test_summarize_disabled_transcript(client):
    """Test handling of videos with disabled transcripts"""
    with patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript') as mock_get_transcript:
        mock_get_transcript.side_effect = TranscriptsDisabled(None)
        
        response = client.post('/api/summarize', json={
            "videoId": "dQw4w9WgXcQ",
            "targetLang": "fr"
        })
        
        assert response.status_code == 403
        assert 'error' in response.json

def test_rate_limiting(client):
    """Test rate limiting functionality"""
    for _ in range(6):  # Exceed the rate limit (5 per minute)
        response = client.post('/api/summarize', json={
            "videoId": "dQw4w9WgXcQ",
            "targetLang": "fr"
        })
    
    assert response.status_code == 429
    assert 'error' in response.json