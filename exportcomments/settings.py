# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import


DEFAULT_BASE_URL = 'https://exportcomments.com/api/v3'


def installed_version():
    """Installed package version for the User-Agent, without pkg_resources.

    ``pkg_resources`` is deprecated and absent on recent Python installs
    (setuptools >= 81 / Python 3.12+ environments) — importing it made the
    whole client fail with ModuleNotFoundError.
    """
    try:
        from importlib.metadata import version  # Python 3.8+
        return version('exportcomments')
    except Exception:
        pass
    try:
        import pkg_resources  # legacy fallback
        return pkg_resources.get_distribution('exportcomments').version
    except Exception:
        return 'noversion'
