# Cristalix API (Python)

Клиентская библиотека для `https://api.cristalix.gg` с аккуратным API и нормальной типизацией. Подходит и для быстрых запросов, и для асинхронных сценариев.

## Что внутри

- Синхронный и асинхронный клиент.
- Типизированные модели ответов.
- Проверка параметров на стороне клиента.

## Установка

```bash
pip install httpx[http2]
```

## Быстрый старт (sync)

```python
from cristalixtop import CristalixClient

client = CristalixClient(
    project_key="YOUR_PROJECT_KEY",
    token="YOUR_TOKEN",
)

profile = client.get_profile_by_name("LisoMandiy")
print(profile)

client.close()
```

## Контекстный менеджер

```python
from cristalixtop import CristalixClient

with CristalixClient(project_key="YOUR_PROJECT_KEY", token="YOUR_TOKEN") as client:
    profiles = client.get_profiles_by_names(["LisoMandiy", "kkp_"])
    print(profiles)
```

## Асинхронный клиент

```python
import asyncio
import httpx
from cristalixtop import AsyncCristalixClient


async def main() -> None:
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    async with AsyncCristalixClient(
        project_key="YOUR_PROJECT_KEY",
        token="YOUR_TOKEN",
        limits=limits,
    ) as client:
        profile = await client.get_profile_by_name("LisoMandiy")
        print(profile)


asyncio.run(main())
```

## Настройка клиента

```python
from cristalixtop import CristalixClient

client = CristalixClient(
    project_key="YOUR_PROJECT_KEY",
    token="YOUR_TOKEN",
    enforce_http2=True,
    max_retries=2,
    timeout=10.0,
)
```

## Обработка ошибок

```python
from cristalixtop import (
    CristalixClient,
    CristalixHTTPError,
    CristalixRateLimitError,
    CristalixValidationError,
)

try:
    with CristalixClient(project_key="YOUR_PROJECT_KEY", token="YOUR_TOKEN") as client:
        client.get_profile_by_name("LisoMandiy")
except CristalixRateLimitError as exc:
    print("Rate limited:", exc.status_code)
except CristalixHTTPError as exc:
    print("HTTP error:", exc.status_code, exc.payload)
except CristalixValidationError as exc:
    print("Bad input:", exc)
```

## Методы

- `get_profiles_by_names(names)` — профили по списку никнеймов (до 50).
- `get_profile_by_name(name)` — профиль по никнейму.
- `get_profiles_by_ids(ids)` — профили по списку UUID (до 50).
- `get_profile_by_id(player_id)` — профиль по UUID.
- `get_profile_reactions(player_id)` — лайки/дизлайки профиля.
- `get_friends(player_id, skip=0, limit=25)` — список друзей с пагинацией.
- `get_subscriptions(player_id, skip=0, limit=25)` — подписчики с пагинацией.
- `get_profile_activity_statistics(player_id)` — активность по играм за текущий день.
- `get_all_profile_statistics(player_id)` — вся статистика по всем периодам.
- `get_profile_statistics(player_id)` — общая статистика без периодов.
- `games_list()` — список игр и режимов.
- `read_by_time_rating(time, game_id, mode_key, sub_mode_key, sort_field, season_key)` — лидерборд по периоду.
