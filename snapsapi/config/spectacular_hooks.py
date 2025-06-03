import logging

logger = logging.getLogger(__name__)


def remove_dj_rest_auth_endpoints(endpoints):
    """
   Filter out endpoints that start with '/dj-rest-auth/' or any other undesired prefix.
   """
    return [ep for ep in endpoints if not ep[0].startswith('/dj-rest-auth/')]


def remove_dj_rest_auth_endpoints(endpoints):
    filtered = []
    for ep in endpoints:
        if ep[0].startswith('/dj-rest-auth/'):
            logger.info(f"🚫 Hiding from schema: {ep[0]}")
            continue
        filtered.append(ep)
    return filtered
