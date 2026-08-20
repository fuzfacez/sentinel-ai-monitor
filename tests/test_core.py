from types import SimpleNamespace
from app.analyzer import fallback_analysis
from app.telegram import incident_message
from app.monitoring import response_failure
import httpx

def test_fallback_for_500():
    result = fallback_analysis(SimpleNamespace(error="Expected HTTP 200", status_code=500, response_time_ms=42))
    assert "серверную ошибку" in result["cause"]

def test_fallback_for_connection():
    result = fallback_analysis(SimpleNamespace(error="ConnectError: refused", status_code=None, response_time_ms=3))
    assert "соединение" in result["cause"]

def test_telegram_escapes_html():
    result = incident_message("<site>", "https://a.test?a=1&b=2", "bad <db>", "restart")
    assert "&lt;site&gt;" in result and "&amp;" in result

def test_expected_text_is_case_insensitive():
    response = httpx.Response(200, text="<title>medCampus</title>")
    monitor = SimpleNamespace(expected_status=200, expected_text="MEDCAMPUS")
    assert response_failure(response, monitor) is None

def test_failure_explains_actual_status():
    response = httpx.Response(403, text="Forbidden")
    monitor = SimpleNamespace(expected_status=200, expected_text=None)
    assert response_failure(response, monitor) == "Получен HTTP 403, ожидался 200"
