"""Async client used by Telegram handlers to talk to the FastAPI API."""

from config import API_BASE_URL


class BackendAPIError(Exception):
    """User-safe error returned by the backend integration."""


async def _request(method, path, **kwargs):
    try:
        import httpx
    except ImportError as exc:
        raise BackendAPIError("Klien backend belum terpasang. Install dependensi bot terlebih dahulu.") from exc

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=15.0) as client:
            response = await client.request(method, path, **kwargs)
    except httpx.RequestError as exc:
        raise BackendAPIError("Backend tidak dapat dihubungi. Coba lagi beberapa saat.") from exc

    if response.is_success:
        return response.json()

    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    if response.status_code == 409:
        if "RCA" in str(detail) or "rca" in str(detail):
            raise BackendAPIError("RCA untuk tiket ini sudah dikirim.")
        raise BackendAPIError(str(detail))
    if response.status_code == 404:
        raise BackendAPIError(str(detail))
    if response.status_code == 422:
        raise BackendAPIError(f"Data RCA tidak valid: {detail}")
    raise BackendAPIError("Backend gagal memproses permintaan. Coba lagi.")


async def get_tickets(telegram_id):
    return await _request("GET", f"/tickets/{telegram_id}")


async def get_engineers(district):
    return await _request("GET", f"/engineers/{district}")


async def get_mock_engineer_tickets(telegram_id):
    return await _request("GET", f"/mock/engineers/{telegram_id}/tickets")


async def get_rca_options():
    return await _request("GET", "/rca-options")


async def submit_rca(ticket_id, rca, rca_detail):
    return await _request("PATCH", f"/tickets/{ticket_id}", json={"rca": rca, "rca_detail": rca_detail})
