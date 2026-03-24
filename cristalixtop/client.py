from __future__ import annotations

import asyncio
import time
from typing import Any, Iterable

import httpx

from .constants import API_BASE_URL, ENDPOINTS, HTTP_VERSIONS_ALLOWED
from .errors import (
    CristalixHTTPError,
    CristalixProtocolError,
    CristalixRateLimitError,
)
from .models import (
    ActivityStatisticsEntry,
    FriendsResponse,
    GameListEntry,
    Profile,
    ProfileReaction,
    StatisticsByPeriodEntry,
    StatisticsEntry,
    TimeRatingEntry,
)
from .types import JsonValue, TimeRange
from .utils import (
    ensure_limit,
    ensure_max_items,
    ensure_non_empty,
    ensure_not_empty,
    ensure_skip,
    to_list,
)


class CristalixClient:
    """High-level client for https://api.cristalix.gg."""

    def __init__(
        self,
        *,
        project_key: str,
        token: str,
        base_url: str = API_BASE_URL,
        timeout: float | httpx.Timeout = 10.0,
        http2: bool = True,
        max_retries: int = 2,
        enforce_http2: bool = True,
        client: httpx.Client | None = None,
    ) -> None:
        ensure_non_empty(project_key, "project_key")
        ensure_non_empty(token, "token")

        self._project_key = project_key
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._enforce_http2 = enforce_http2

        if client is None:
            self._owns_client = True
            self._client = httpx.Client(
                base_url=self._base_url,
                timeout=self._timeout,
                http2=http2,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                },
            )
        else:
            self._owns_client = False
            self._client = client

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "CristalixClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _build_params(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        out: dict[str, Any] = {"project_key": self._project_key}
        if params:
            out.update(params)
        return out

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: JsonValue | None = None,
    ) -> JsonValue:
        attempts = 0
        while True:
            response = self._client.request(
                method,
                path,
                params=self._build_params(params),
                json=json_body,
            )
            if self._enforce_http2 and response.http_version not in HTTP_VERSIONS_ALLOWED:
                raise CristalixProtocolError(
                    f"unsupported HTTP version: {response.http_version}",
                )

            if response.status_code == 429:
                if attempts >= self._max_retries:
                    raise CristalixRateLimitError(
                        "rate limit exceeded",
                        status_code=response.status_code,
                        payload=_safe_json(response),
                    )
                attempts += 1
                delay = _retry_delay_seconds(response, attempts)
                time.sleep(delay)
                continue

            if response.status_code >= 400:
                raise CristalixHTTPError(
                    f"request failed with status {response.status_code}",
                    status_code=response.status_code,
                    payload=_safe_json(response),
                )
            return _safe_json(response)

    def get_profiles_by_names(self, names: Iterable[str]) -> list[Profile]:
        """Return basic profiles by usernames (max 50)."""
        payload = to_list(names)
        ensure_not_empty(payload, "names")
        ensure_max_items(payload, 50, "names")
        return self._request(
            "GET",
            ENDPOINTS["profiles_by_names"],
            json_body={"array": payload},
        )

    def get_profile_by_name(self, name: str) -> Profile:
        """Return basic profile by username."""
        ensure_non_empty(name, "name")
        return self._request(
            "GET",
            ENDPOINTS["profile_by_name"],
            params={"playerName": name},
        )

    def get_profiles_by_ids(self, ids: Iterable[str]) -> list[Profile]:
        """Return basic profiles by player UUIDs (max 50)."""
        payload = to_list(ids)
        ensure_not_empty(payload, "ids")
        ensure_max_items(payload, 50, "ids")
        return self._request(
            "GET",
            ENDPOINTS["profiles_by_ids"],
            json_body={"array": payload},
        )

    def get_profile_by_id(self, player_id: str) -> Profile:
        """Return basic profile by player UUID."""
        ensure_non_empty(player_id, "player_id")
        return self._request(
            "GET",
            ENDPOINTS["profile_by_id"],
            params={"playerId": player_id},
        )

    def get_profile_reactions(self, player_id: str) -> ProfileReaction:
        """Return profile likes and dislikes."""
        ensure_non_empty(player_id, "player_id")
        return self._request(
            "GET",
            ENDPOINTS["profile_reactions"],
            params={"playerId": player_id},
        )

    def get_friends(self, player_id: str, *, skip: int = 0, limit: int = 25) -> FriendsResponse:
        """Return friends list with pagination."""
        ensure_non_empty(player_id, "player_id")
        ensure_skip(skip)
        ensure_limit(limit, max_limit=100)
        return self._request(
            "GET",
            ENDPOINTS["friends"],
            params={"playerId": player_id, "skip": skip, "limit": limit},
        )

    def get_subscriptions(self, player_id: str, *, skip: int = 0, limit: int = 25) -> FriendsResponse:
        """Return subscriptions list with pagination."""
        ensure_non_empty(player_id, "player_id")
        ensure_skip(skip)
        ensure_limit(limit, max_limit=100)
        return self._request(
            "GET",
            ENDPOINTS["subscriptions"],
            params={"playerId": player_id, "skip": skip, "limit": limit},
        )

    def get_profile_activity_statistics(self, player_id: str) -> list[ActivityStatisticsEntry]:
        """Return per-mode stats for the current day."""
        ensure_non_empty(player_id, "player_id")
        return self._request(
            "GET",
            ENDPOINTS["activity_stats"],
            params={"playerId": player_id},
        )

    def get_all_profile_statistics(self, player_id: str) -> list[StatisticsByPeriodEntry]:
        """Return full statistics across all available periods."""
        ensure_non_empty(player_id, "player_id")
        return self._request(
            "GET",
            ENDPOINTS["all_stats"],
            params={"playerId": player_id},
        )

    def get_profile_statistics(self, player_id: str) -> list[StatisticsEntry]:
        """Return full statistics without period splits."""
        ensure_non_empty(player_id, "player_id")
        return self._request(
            "GET",
            ENDPOINTS["stats"],
            params={"playerId": player_id},
        )

    def games_list(self) -> list[GameListEntry]:
        """Return list of all games, modes, and stat fields."""
        return self._request(
            "GET",
            ENDPOINTS["games_list"],
        )

    def read_by_time_rating(
        self,
        *,
        time: TimeRange,
        game_id: str,
        mode_key: str,
        sub_mode_key: str,
        sort_field: str,
        season_key: str,
    ) -> list[TimeRatingEntry]:
        """Return leaderboard by time range and mode."""
        ensure_non_empty(game_id, "game_id")
        ensure_non_empty(mode_key, "mode_key")
        ensure_non_empty(sub_mode_key, "sub_mode_key")
        ensure_non_empty(sort_field, "sort_field")
        ensure_non_empty(season_key, "season_key")
        return self._request(
            "GET",
            ENDPOINTS["time_rating"],
            params={
                "time": time,
                "gameId": game_id,
                "modeKey": mode_key,
                "subModeKey": sub_mode_key,
                "sortField": sort_field,
                "seasonKey": season_key,
            },
        )


class AsyncCristalixClient:
    """High-performance async client for https://api.cristalix.gg."""

    def __init__(
        self,
        *,
        project_key: str,
        token: str,
        base_url: str = API_BASE_URL,
        timeout: float | httpx.Timeout = 10.0,
        http2: bool = True,
        max_retries: int = 2,
        enforce_http2: bool = True,
        limits: httpx.Limits | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        ensure_non_empty(project_key, "project_key")
        ensure_non_empty(token, "token")

        self._project_key = project_key
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._enforce_http2 = enforce_http2

        if client is None:
            self._owns_client = True
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                http2=http2,
                limits=limits,
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Content-Type": "application/json",
                },
            )
        else:
            self._owns_client = False
            self._client = client

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> "AsyncCristalixClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    def _build_params(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        out: dict[str, Any] = {"project_key": self._project_key}
        if params:
            out.update(params)
        return out

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: JsonValue | None = None,
    ) -> JsonValue:
        attempts = 0
        while True:
            response = await self._client.request(
                method,
                path,
                params=self._build_params(params),
                json=json_body,
            )
            if self._enforce_http2 and response.http_version not in HTTP_VERSIONS_ALLOWED:
                raise CristalixProtocolError(
                    f"unsupported HTTP version: {response.http_version}",
                )

            if response.status_code == 429:
                if attempts >= self._max_retries:
                    raise CristalixRateLimitError(
                        "rate limit exceeded",
                        status_code=response.status_code,
                        payload=_safe_json(response),
                    )
                attempts += 1
                delay = _retry_delay_seconds(response, attempts)
                await _async_sleep(delay)
                continue

            if response.status_code >= 400:
                raise CristalixHTTPError(
                    f"request failed with status {response.status_code}",
                    status_code=response.status_code,
                    payload=_safe_json(response),
                )
            return _safe_json(response)

    async def get_profiles_by_names(self, names: Iterable[str]) -> list[Profile]:
        payload = to_list(names)
        ensure_not_empty(payload, "names")
        ensure_max_items(payload, 50, "names")
        return await self._request(
            "GET",
            ENDPOINTS["profiles_by_names"],
            json_body={"array": payload},
        )

    async def get_profile_by_name(self, name: str) -> Profile:
        ensure_non_empty(name, "name")
        return await self._request(
            "GET",
            ENDPOINTS["profile_by_name"],
            params={"playerName": name},
        )

    async def get_profiles_by_ids(self, ids: Iterable[str]) -> list[Profile]:
        payload = to_list(ids)
        ensure_not_empty(payload, "ids")
        ensure_max_items(payload, 50, "ids")
        return await self._request(
            "GET",
            ENDPOINTS["profiles_by_ids"],
            json_body={"array": payload},
        )

    async def get_profile_by_id(self, player_id: str) -> Profile:
        ensure_non_empty(player_id, "player_id")
        return await self._request(
            "GET",
            ENDPOINTS["profile_by_id"],
            params={"playerId": player_id},
        )

    async def get_profile_reactions(self, player_id: str) -> ProfileReaction:
        ensure_non_empty(player_id, "player_id")
        return await self._request(
            "GET",
            ENDPOINTS["profile_reactions"],
            params={"playerId": player_id},
        )

    async def get_friends(self, player_id: str, *, skip: int = 0, limit: int = 25) -> FriendsResponse:
        ensure_non_empty(player_id, "player_id")
        ensure_skip(skip)
        ensure_limit(limit, max_limit=100)
        return await self._request(
            "GET",
            ENDPOINTS["friends"],
            params={"playerId": player_id, "skip": skip, "limit": limit},
        )

    async def get_subscriptions(self, player_id: str, *, skip: int = 0, limit: int = 25) -> FriendsResponse:
        ensure_non_empty(player_id, "player_id")
        ensure_skip(skip)
        ensure_limit(limit, max_limit=100)
        return await self._request(
            "GET",
            ENDPOINTS["subscriptions"],
            params={"playerId": player_id, "skip": skip, "limit": limit},
        )

    async def get_profile_activity_statistics(self, player_id: str) -> list[ActivityStatisticsEntry]:
        ensure_non_empty(player_id, "player_id")
        return await self._request(
            "GET",
            ENDPOINTS["activity_stats"],
            params={"playerId": player_id},
        )

    async def get_all_profile_statistics(self, player_id: str) -> list[StatisticsByPeriodEntry]:
        ensure_non_empty(player_id, "player_id")
        return await self._request(
            "GET",
            ENDPOINTS["all_stats"],
            params={"playerId": player_id},
        )

    async def get_profile_statistics(self, player_id: str) -> list[StatisticsEntry]:
        ensure_non_empty(player_id, "player_id")
        return await self._request(
            "GET",
            ENDPOINTS["stats"],
            params={"playerId": player_id},
        )

    async def games_list(self) -> list[GameListEntry]:
        return await self._request(
            "GET",
            ENDPOINTS["games_list"],
        )

    async def read_by_time_rating(
        self,
        *,
        time: TimeRange,
        game_id: str,
        mode_key: str,
        sub_mode_key: str,
        sort_field: str,
        season_key: str,
    ) -> list[TimeRatingEntry]:
        ensure_non_empty(game_id, "game_id")
        ensure_non_empty(mode_key, "mode_key")
        ensure_non_empty(sub_mode_key, "sub_mode_key")
        ensure_non_empty(sort_field, "sort_field")
        ensure_non_empty(season_key, "season_key")
        return await self._request(
            "GET",
            ENDPOINTS["time_rating"],
            params={
                "time": time,
                "gameId": game_id,
                "modeKey": mode_key,
                "subModeKey": sub_mode_key,
                "sortField": sort_field,
                "seasonKey": season_key,
            },
        )


def _safe_json(response: httpx.Response) -> JsonValue:
    try:
        return response.json()
    except ValueError:
        return response.text


def _retry_delay_seconds(response: httpx.Response, attempts: int) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return max(float(retry_after), 0.0)
        except ValueError:
            pass
    return min(2.0 ** attempts, 10.0)


async def _async_sleep(seconds: float) -> None:
    if seconds <= 0:
        return
    await asyncio.sleep(seconds)
