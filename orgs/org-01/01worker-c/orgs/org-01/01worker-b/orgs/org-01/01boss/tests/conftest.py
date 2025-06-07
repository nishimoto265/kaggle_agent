# -*- coding: utf-8 -*-
"""
pytest設定ファイル
"""
import pytest
import asyncio
from pathlib import Path

@pytest.fixture(scope="session")
def event_loop():
    """セッション全体で使用するイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def project_root():
    """プロジェクトルートディレクトリ"""
    return Path(__file__).parent.parent
