import pytest
from unittest.mock import patch, MagicMock

def test_timestamped_summary_success(client, mock_openai, mock_youtube_transcript_api):
    """Test successful timestamped summary generation"""
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"keyMoments": [{"title": "Test", "description": "Test desc", "importance": "High"}]}'
                )
            )
        ]
    )

    with patch('app.client', mock_openai), \
         patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript', mock_youtube_transcript_api):
        
        response = client.post('/api/timestamped-summary', json={
            "videoId": "dQw4w9WgXcQ",
            "targetLang": "fr"
        })
        
        assert response.status_code == 200
        data = response.json
        assert 'analysis' in data
        assert 'timestamps' in data
        assert len(data['timestamps']) > 0

def test_enhanced_transcript_success(client, mock_openai, mock_youtube_transcript_api):
    """Test successful enhanced transcript generation"""
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"enhancedTranscript": "Test transcript", "sections": ["Intro", "Main"], "readabilityScore": "8/10"}'
                )
            )
        ]
    )

    with patch('app.client', mock_openai), \
         patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript', mock_youtube_transcript_api):
        
        response = client.post('/api/enhanced-transcript', json={
            "videoId": "dQw4w9WgXcQ",
            "targetLang": "fr"
        })
        
        assert response.status_code == 200
        data = response.json
        assert 'result' in data
        assert 'enhancedTranscript' in data['result']
        assert 'sections' in data['result']
        assert 'readabilityScore' in data['result']

def test_top_comments_success(client, mock_openai, mock_youtube_transcript_api):
    """Test successful top comments analysis"""
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"topComments": [{"username": "Test", "comment": "Great video", "likes": 100, "relevance": "9/10"}], "analysisInsights": "Positive feedback"}'
                )
            )
        ]
    )

    with patch('app.client', mock_openai), \
         patch('youtube_transcript_api.YouTubeTranscriptApi.get_transcript', mock_youtube_transcript_api):
        
        response = client.post('/api/top-comments', json={
            "videoId": "dQw4w9WgXcQ"
        })
        
        assert response.status_code == 200
        data = response.json
        assert 'result' in data
        assert 'topComments' in data['result']
        assert 'analysisInsights' in data['result']

@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/timestamped-summary",
        "/api/enhanced-transcript",
        "/api/top-comments"
    ]
)
def test_invalid_requests(client, endpoint):
    """Test invalid requests for all endpoints"""
    # Test missing videoId
    response = client.post(endpoint, json={})
    assert response.status_code == 400
    assert 'error' in response.json

    # Test invalid video ID format
    response = client.post(endpoint, json={"videoId": "invalid"})
    assert response.status_code == 400
    assert 'error' in response.json

def test_error_handling(client, mock_openai):
    """Test error handling when OpenAI API fails"""
    mock_openai.chat.completions.create.side_effect = Exception("API Error")

    with patch('app.client', mock_openai):
        endpoints = [
            "/api/summarize",
            "/api/timestamped-summary",
            "/api/enhanced-transcript",
            "/api/top-comments"
        ]
        
        for endpoint in endpoints:
            response = client.post(endpoint, json={
                "videoId": "dQw4w9WgXcQ",
                "targetLang": "fr"
            })
            
            assert response.status_code == 500
            assert 'error' in response.json