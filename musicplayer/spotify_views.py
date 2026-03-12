import base64, time, requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

_token_cache = {"access_token": None, "expires_at": 0}

@require_GET
def spotify_token(request):
    if time.time() < _token_cache["expires_at"] - 30:
        return JsonResponse({"access_token": _token_cache["access_token"], "expires_in": 3600})

    creds = base64.b64encode(
        f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()

    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {creds}"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": settings.SPOTIFY_REFRESH_TOKEN,
        },
    )
    resp.raise_for_status()
    data = resp.json()
    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data["expires_in"]
    return JsonResponse({"access_token": data["access_token"], "expires_in": data["expires_in"]})