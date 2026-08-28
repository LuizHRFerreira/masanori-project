#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    from django.core.management import execute_from_command_line

    has_server_address = any(not argument.startswith('-') for argument in sys.argv[2:])
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver' and not has_server_address:
        sys.argv.append('127.0.0.1:8001')

    execute_from_command_line(sys.argv)
