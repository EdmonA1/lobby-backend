def apply_filters(current_user: dict, candidate: dict) -> bool:
    if candidate["telegram_id"] == current_user["telegram_id"]:
        return False
    viewed = current_user.get("viewed_profiles", [])
    if candidate["telegram_id"] in viewed:
        return False
    filter_gender = current_user.get("filter_gender", "any")
    if filter_gender and filter_gender != "any":
        if candidate.get("gender") != filter_gender:
            return False
    age_min = current_user.get("filter_age_min", 18)
    age_max = current_user.get("filter_age_max", 60)
    candidate_age = candidate.get("age", 0)
    if not (age_min <= candidate_age <= age_max):
        return False
    return True

def get_swipe_candidates(current_user: dict, all_users: dict) -> list:
    candidates = []
    for uid, user in all_users.items():
        if apply_filters(current_user, user):
            candidates.append(user)
    candidates.sort(
        key=lambda u: len(set(u.get("games", [])) & set(current_user.get("games", []))),
        reverse=True
    )
    return candidates[:20]
