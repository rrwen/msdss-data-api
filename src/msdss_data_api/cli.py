import argparse

def _get_parser():
    """
    Builds an ``argparse`` parser for the ``msdss-data`` command line tool.

    Returns
    -------
    :class:`argparse.ArgumentParser`
        An ``argparse`` parser for ``msdss-data``.

    Author
    ------
    Richard Wen <rrwen.dev@gmail.com>

    Example
    -------

    .. jupyter-execute::
        :hide-output:

        from msdss_data_api.cli import _get_parser

        parser = _get_parser()
        parser.print_help()
    """

    # (_get_parser_parsers) Create main parser and sub parsers
    parser = argparse.ArgumentParser(description='Manages data with a database')
    subparsers = parser.add_subparsers(title='commands', dest='command')
    
    # (_get_parser_register) Add register command
    register_parser = subparsers.add_parser('register', help='register a user')
    register_parser.add_argument('email', type=str, nargs='?', help='email for user')
    register_parser.add_argument('password', type=str, nargs='?', help='password for user')
    register_parser.add_argument('--superuser', dest='superuser', action='store_true', help='register a superuser')
    register_parser.set_defaults(superuser=False)

    # (_get_parser_get) Add get command
    get_parser = subparsers.add_parser('get', help='get user attributes')
    get_parser.add_argument('email', type=str, help='email for user')

    # (_get_parser_delete) Add delete command
    delete_parser = subparsers.add_parser('delete', help='delete a user')
    delete_parser.add_argument('email', type=str, help='email of user to delete')

    # (_get_parser_reset) Add reset command
    reset_parser = subparsers.add_parser('reset', help='reset user password')
    reset_parser.add_argument('email', type=str, help='email of user to reset')
    reset_parser.add_argument('password', type=str, nargs='?', help='new password to use')

    # (_get_parser_update) Add update command
    update_parser = subparsers.add_parser('update', help='update a user\'s attribute')
    update_parser.add_argument('email', type=str, help='email of user')
    update_parser.add_argument('--is_active', type=bool, default=None, help='set is_active attribute')
    update_parser.add_argument('--is_superuser', type=bool, default=None, help='set is_superuser attribute')
    update_parser.add_argument('--is_verified', type=bool, default=None, help='set is_verified attribute')

    # (_get_parser_start) Add start command
    start_parser = subparsers.add_parser('start', help='start a users api server')
    start_parser.add_argument('--host', type=str, default='127.0.0.1', help='address to host server')
    start_parser.add_argument('--port', type=int, default=8000, help='port to host server')
    start_parser.add_argument('--log_level', type=str, default='info', help='level of verbose messages to display')
    start_parser.add_argument('--disable_data_router', dest='enable_data_router', action='store_false', help='disable data router')
    start_parser.add_argument('--enable_users', dest='enable_users', action='store_true', help='disable users authentication')
    start_parser.set_defaults(
        enable_data_router=True,
        enable_users=False
    )

    # (_get_parser_file_key) Add file and key arguments to all commands
    for p in [parser, register_parser, delete_parser, update_parser, get_parser, reset_parser, start_parser]:
        p.add_argument('--env_file', type=str, default='./.env', help='path of .env file')
        p.add_argument('--key_path', type=str, default=None, help='path of key file')
    
    # (_get_parser_out) Return the parser
    out = parser
    return out