import pytest
from diff_visualizer import DiffVisualizer

def test_diff_stats():
    diff_visualizer = DiffVisualizer()

    before_text = """Welcome to Edica Naturals
    We offer the finest natural skincare products."""

    after_text = """Welcome to Edica Naturals - Your Natural Beauty Partner
    We offer the finest natural and organic skincare products."""

    stats = diff_visualizer.get_diff_stats(before_text, after_text)

    assert isinstance(stats, dict)
    assert 'words_added' in stats
    assert 'words_removed' in stats
    assert 'total_changes' in stats
    assert stats['words_added'] >= 0
    assert stats['words_removed'] >= 0
    assert stats['total_changes'] == stats['words_added'] + stats['words_removed']

def test_empty_text_diff():
    diff_visualizer = DiffVisualizer()
    stats = diff_visualizer.get_diff_stats("", "")

    assert stats['words_added'] == 0
    assert stats['words_removed'] == 0
    assert stats['total_changes'] == 0

def test_complete_text_change():
    diff_visualizer = DiffVisualizer()
    stats = diff_visualizer.get_diff_stats(
        "Original text",
        "Completely different text"
    )

    assert stats['words_added'] > 0
    assert stats['words_removed'] > 0
    assert stats['total_changes'] > 0