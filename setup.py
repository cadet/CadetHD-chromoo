#!/usr/bin/env python

import setuptools

def git_version():
    """ Return version with local version identifier. """
    import git
    repo = git.Repo('.git')
    repo.git.status()
    print(repo)
    sha = repo.head.commit.hexsha
    sha = repo.git.rev_parse(sha, short=6)
    print(sha)
    if repo.is_dirty():
        return '{sha}.dirty'.format(sha=sha)
    else:
        return sha

if __name__ == "__main__":
    setuptools.setup(version=git_version())
