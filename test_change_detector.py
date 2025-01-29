import pytest
from change_detector import ChangeDetector
from datetime import datetime

def test_change_detection():
    detector = ChangeDetector()
    
    # Test data
    previous_content = {
        'text': 'Welcome to our store',
        'pages': [
            {'url': 'example.com', 'location': '/'}
        ]
    }
    
    current_content = {
        'text': 'Welcome to our updated store',
        'pages': [
            {'url': 'example.com', 'location': '/'},
            {'url': 'example.com/new', 'location': '/new'}
        ]
    }
    
    # Initialize the detector with previous content
    detector.previous_content = previous_content
    
    # Detect changes
    changes = detector.detect_changes(current_content)
    
    # Verify changes are detected correctly
    assert isinstance(changes, list)
    assert len(changes) > 0
    
    # Check change properties
    text_changes = [c for c in changes if c['type'] == 'text_change']
    assert len(text_changes) > 0
    assert 'timestamp' in text_changes[0]
    assert isinstance(datetime.fromisoformat(text_changes[0]['timestamp']), datetime)

def test_no_changes():
    detector = ChangeDetector()
    
    content = {
        'text': 'Welcome to our store',
        'pages': [{'url': 'example.com', 'location': '/'}]
    }
    
    # Set the same content as previous and current
    detector.previous_content = content
    changes = detector.detect_changes(content)
    
    # Should only include the site_check change
    assert len(changes) == 1
    assert changes[0]['type'] == 'site_check'

def test_new_page_detection():
    detector = ChangeDetector()
    
    # Previous content with one page
    previous = {
        'text': 'content',
        'pages': [{'url': 'example.com', 'location': '/'}]
    }
    
    # Current content with a new page
    current = {
        'text': 'content',
        'pages': [
            {'url': 'example.com', 'location': '/'},
            {'url': 'example.com/about', 'location': '/about'}
        ]
    }
    
    detector.previous_content = previous
    changes = detector.detect_changes(current)
    
    # Should detect the new page
    page_changes = [c for c in changes if c['type'] == 'page_added']
    assert len(page_changes) > 0
    assert page_changes[0]['location'] == '/about'

def test_removed_page_detection():
    detector = ChangeDetector()
    
    # Previous content with two pages
    previous = {
        'text': 'content',
        'pages': [
            {'url': 'example.com', 'location': '/'},
            {'url': 'example.com/about', 'location': '/about'}
        ]
    }
    
    # Current content with one page removed
    current = {
        'text': 'content',
        'pages': [{'url': 'example.com', 'location': '/'}]
    }
    
    detector.previous_content = previous
    changes = detector.detect_changes(current)
    
    # Should detect the removed page
    page_changes = [c for c in changes if c['type'] == 'page_removed']
    assert len(page_changes) > 0
    assert page_changes[0]['location'] == '/about'

def test_first_run():
    detector = ChangeDetector()
    
    # Test first run with no previous content
    detector.previous_content = None
    current = {
        'text': 'Welcome',
        'pages': [{'url': 'example.com', 'location': '/'}]
    }
    
    changes = detector.detect_changes(current)
    
    # Should only include initial site check
    assert len(changes) == 1
    assert changes[0]['type'] == 'site_check'
    assert 'pages' in changes[0]
