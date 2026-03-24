API_BASE_URL = "https://api.cristalix.gg"

HTTP_VERSIONS_ALLOWED = {"HTTP/2", "HTTP/3"}

ENDPOINTS = {
    "profiles_by_names": "/players/v1/getProfilesByNames",
    "profile_by_name": "/players/v1/getProfileByName",
    "profiles_by_ids": "/players/v1/getProfilesByIds",
    "profile_by_id": "/players/v1/getProfileById",
    "profile_reactions": "/players/v1/getProfileReactions",
    "friends": "/players/v1/getFriends",
    "subscriptions": "/players/v1/getSubscriptions",
    "activity_stats": "/statistics/v1/getProfileActivityStatistics",
    "all_stats": "/statistics/v1/getAllProfileStatistics",
    "stats": "/statistics/v1/getProfileStatistics",
    "games_list": "/statistics/v1/gamesList",
    "time_rating": "/statistics/v1/readByTimeRating",
}
