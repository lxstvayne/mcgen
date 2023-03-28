from cement import App, init_defaults
from cement.core.exc import CaughtSignal

from .controllers.base import Base, package_metadata, Generate
from .core.exc import MyAppError

# configuration defaults
CONFIG = init_defaults(package_metadata.name)


class CliApp(App):
    class Meta:
        label = package_metadata.name

        # configuration defaults
        config_defaults = CONFIG

        # call sys.exit() on close
        exit_on_close = True

        # load additional framework extensions
        extensions = [
            'colorlog',
        ]

        # set the log handler
        log_handler = 'colorlog'

        # register handlers
        handlers = [
            Base,
            Generate
        ]


def main():
    with CliApp() as app:
        try:
            app.run()

        except AssertionError as e:
            print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except MyAppError as e:
            print('MyAppError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0
