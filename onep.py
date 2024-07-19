import re
# Adapted for 音声作品 from aniep by Soruly
# (https://github.com/soruly/aniep/blob/master/src/index.js)


def onep(string: str) -> str | None:

    pat = re.findall(r'_\d+_', string)  # _13_
    if not pat == []:
        episode = re.findall(r'\d+', str(pat))[0]
        return episode

    pat = re.findall(r'\d+_', string)  # 13_
    if not pat == []:
        episode = re.findall(r'\d+', str(pat))[0]
        return episode

    pat = re.findall(r'_\d+', string)  # _13
    if not pat == []:
        episode = re.findall(r'\d+', str(pat))[0]
        return episode

    pat = re.findall(r'\d+.', string)  # 13.
    if not pat == []:
        episode = re.findall(r'\d+', str(pat))[0]
        return episode

    pat = re.findall(r'\d+-', string)  # 13-
    if not pat == []:
        episode = re.findall(r'\d+', str(pat))[0]
        return episode

    pat = re.findall(r'tr\d+', string.lower())  # tr13
    if not pat == []:
        episode = re.findall(r'\d+', str(pat))[0]
        return episode

    pat = re.findall(r'track\d+', string.lower())  # track13
    if not pat == []:
        episode = re.findall(r'\d+', str(pat))[0]
        return episode
