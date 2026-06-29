Run # Usamos timeout para garantir que o job não fique travado infinitamente se um processo pendurar
  # Usamos timeout para garantir que o job não fique travado infinitamente se um processo pendurar
  timeout 5m pytest --cov-report=xml
  shell: /usr/bin/bash -e {0}
  env:
    pythonLocation: /opt/hostedtoolcache/Python/3.11.15/x64
    PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib/pkgconfig
    Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
    Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
    Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.11.15/x64
    LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.11.15/x64/lib
    ENVIRONMENT: test
    TELEGRAM_BOT_TOKEN: ***
    TELEGRAM_ALLOWED_USER_IDS: ***
ImportError while loading conftest '/home/runner/work/QAgent/QAgent/tests/conftest.py'.
tests/conftest.py:3: in <module>
    from core.bot import bot
E   ModuleNotFoundError: No module named 'core'
Error: Process completed with exit code 4.