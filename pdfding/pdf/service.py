from .models import Tag
from users.models import Profile


def process_tag_names(tag_names: list[str], owner_profile: Profile) -> list[Tag]:
    """
    Process the specified tags. If the tag is existing it will simply be added to the return list. If it does not
    exist it, it will be created and then be added to the return list.
    """

    tags = []
    for tag_name in tag_names:
        try:
            tag = Tag.objects.get(owner=owner_profile, name=tag_name)
        except Tag.DoesNotExist:
            tag = Tag.objects.create(name=tag_name, owner=owner_profile)

        tags.append(tag)

    return tags


def process_raw_search_query(raw_search_query: str) -> tuple[str, list[str]]:
    """
    Process the raw search query.

    Example input: #tag1 #tag2 searchstring1 searchstring2
    Example output: ('searchstring1 searchstring2', ['tag1', 'tag2'])
    """

    search = []
    tags = []

    if raw_search_query:
        split_query = raw_search_query.split(sep=' ')

        for query in split_query:
            if query.startswith('#'):
                # ignore hashtags only
                if len(query) > 1:
                    tags.append(query[1:])
            elif query:
                search.append(query)

    search = ' '.join(search)

    return search, tags
