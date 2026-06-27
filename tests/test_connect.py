"""Tests for client mode: connect() builds a PLCClient and spawns nothing."""

from __future__ import annotations

import subprocess

from gomc_rest_client import PLCClient

import gomc_rest


def test_connect_returns_client_with_url_and_token():
    plc = gomc_rest.connect("http://plc.example:8080", token="tok123")
    assert isinstance(plc, PLCClient)
    assert plc.base_url == "http://plc.example:8080"
    assert plc._auth_headers.get("Authorization") == "Bearer tok123"


def test_connect_without_token_sends_no_auth():
    plc = gomc_rest.connect("http://plc.example:8080")
    assert not plc._auth_headers


def test_connect_does_not_spawn_subprocess(monkeypatch):
    def _boom(*args, **kwargs):
        raise AssertionError("connect() must not start a subprocess")

    monkeypatch.setattr(subprocess, "Popen", _boom)
    assert isinstance(gomc_rest.connect("http://plc.example:8080"), PLCClient)
