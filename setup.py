#!/usr/bin/env python

import setuptools
import git

def git_version():
    """ Return version with local version identifier. """
    repo = git.Repo('.', search_parent_directories=True)
    repo.git.status()
    sha = repo.head.commit.hexsha
    sha = repo.git.rev_parse(sha, short=6)
    if repo.is_dirty():
        return '{sha}.dirty'.format(sha=sha)
    else:
        return sha

if __name__ == "__main__":
    setuptools.setup(version="0.1")
