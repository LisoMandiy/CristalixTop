from __future__ import annotations

from typing import TypedDict


class Group(TypedDict, total=False):
    key: str
    name: str
    prefixColor: str
    nameColor: str
    staffGroup: bool
    default: bool


class Donate(TypedDict, total=False):
    key: str
    name: str
    prefixColor: str
    nameColor: str
    staffGroup: bool
    default: bool


class Textures(TypedDict, total=False):
    skin: str
    cloak: str


class Profile(TypedDict, total=False):
    id: str
    username: str
    registerTime: str
    group: Group
    donate: Donate
    textures: Textures
    realm: str
    lastJoinTime: str
    lastQuitTime: str
    onlineTime: int


class ProfileReaction(TypedDict):
    likes: int
    dislikes: int


class FriendEntry(TypedDict, total=False):
    playerId: str
    groupName: str
    username: str
    realm: str
    lastJoinTime: str
    lastQuitTime: str


class FriendsResponse(TypedDict):
    list: list[FriendEntry]
    totalCount: int


class GameField(TypedDict, total=False):
    key: str
    name: str
    type: str


class GameMode(TypedDict, total=False):
    key: str
    name: str
    description: str
    fields: list[GameField]


class GameListEntry(TypedDict, total=False):
    gameId: str
    title: str
    description: str
    season: str
    released: bool
    status: str
    icon: str
    modes: list[GameMode]
    updatedAt: str
    createdAt: str


class StatisticsEntry(TypedDict, total=False):
    gameId: str
    modeKey: str
    subModeKey: str
    seasonKey: str
    statistics: dict[str, int]


class ActivityStatisticsEntry(TypedDict, total=False):
    gameId: str
    modeKey: str
    subModeKey: str
    seasonKey: str
    statistics: dict[str, int]


class StatisticsByPeriodEntry(TypedDict, total=False):
    gameId: str
    modeKey: str
    subModeKey: str
    seasonKey: str
    statisticsByPeriod: dict[str, dict[str, int]]
    periodEndings: dict[str, int]


class TimeRatingEntry(TypedDict, total=False):
    playerId: str
    username: str
    statistics: dict[str, int]
    periodEnding: int
