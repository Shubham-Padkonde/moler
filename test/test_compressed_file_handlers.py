"""Regression tests for compressed log file paths."""

from unittest.mock import patch

import pytest

from moler.util.compressed_rotating_file_handler import CompressedRotatingFileHandler
from moler.util.compressed_timed_rotating_file_handler import CompressedTimedRotatingFileHandler


@pytest.mark.parametrize('handler_class', [CompressedRotatingFileHandler, CompressedTimedRotatingFileHandler])
@pytest.mark.parametrize('name', ['plain.log', 'log with spaces.log', "quoted'log.log"])
def test_compression_preserves_file_arguments(tmp_path, handler_class, name):
    filename = tmp_path / name
    filename.touch()
    handler = handler_class(filename=str(filename), delay=True)
    with patch('subprocess.Popen') as popen:
        try:
            handler._compress_file(str(filename))
            popen.assert_called_once_with(['zip', '-9mq', str(filename) + '.zip', str(filename)])
        finally:
            handler.close()


@pytest.mark.parametrize('handler_class', [CompressedRotatingFileHandler, CompressedTimedRotatingFileHandler])
def test_compression_preserves_quoted_command_arguments(tmp_path, handler_class):
    filename = tmp_path / 'test.log'
    filename.touch()
    handler = handler_class(filename=str(filename), delay=True,
                            compress_command='"custom compressor" --label "test logs" {compressed} {log_input}')
    with patch('subprocess.Popen') as popen:
        try:
            handler._compress_file(str(filename))
            popen.assert_called_once_with(['custom compressor', '--label', 'test logs',
                                          str(filename) + '.zip', str(filename)])
        finally:
            handler.close()
