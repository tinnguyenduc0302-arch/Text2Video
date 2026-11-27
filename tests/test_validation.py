import pytest
from app.core.validation import parse_srt
from app.core.pipeline import output_path

def test_srt_vietnamese_bom(tmp_path):
    path = tmp_path / 'phụ đề.srt'
    path.write_text('1\n00:00:00,000 --> 00:00:01,000\nXin chào\n', encoding='utf-8-sig')
    assert parse_srt(path, 1.0)[0][2] == 'Xin chào'

def test_srt_over_audio_reports_entry(tmp_path):
    path = tmp_path / 'bad.srt'
    path.write_text('1\n00:00:00,000 --> 00:00:02,000\nHello\n', encoding='utf-8')
    with pytest.raises(ValueError, match='mục 1'):
        parse_srt(path, 1.0)

def test_output_name_no_overwrite(tmp_path):
    first = output_path(tmp_path)
    first.touch()
    assert output_path(tmp_path) != first
