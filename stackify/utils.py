import os


def arg_or_env(name, args, default=None):
    env_name = 'STACKIFY_{0}'.format(name.upper())
    try:
        value = args.get(name)
        if not value:
            value = os.environ[env_name]
        return value
    except KeyError:
        if default:
            return default
        else:
            raise NameError('You must specify the keyword argument {0} or environment variable {1}'.format(name, env_name))
