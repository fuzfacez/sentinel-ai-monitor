from types import SimpleNamespace
from app.analyzer import fallback_analysis
from app.telegram import incident_message

def test_fallback_for_500():
    result = fallback_analysis(SimpleNamespace(error="Expected HTTP 200", status_code=500, response_time_ms=42))
    assert "серверную ошибку" in result["cause"]

def test_fallback_for_connection():
    result = fallback_analysis(SimpleNamespace(error="ConnectError: refused", status_code=None, response_time_ms=3))
    assert "соединение" in result["cause"]

def test_telegram_escapes_html():
    result = incident_message("<site>", "https://a.test?a=1&b=2", "bad <db>", "restart")
    assert "&lt;site&gt;" in result and "&amp;" in result

