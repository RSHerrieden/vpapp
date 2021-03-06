def __to_version(release):
    v = release.split("-")
    return v[0]

def __is_develop(release):
    return release.endswith("-dev")

name = "vpapp"
release = "0.1.3"
__version__ = __to_version(release)
__develop__ = __is_develop(release)
