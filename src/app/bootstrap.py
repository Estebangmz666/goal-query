from dataclasses import dataclass

try:
    from src.app.environment import load_environment_file
    from src.app.settings import ApplicationSettings, load_application_settings
except ModuleNotFoundError:
    from app.environment import load_environment_file
    from app.settings import ApplicationSettings, load_application_settings


@dataclass(frozen=True)
class ApplicationContext:
    settings: ApplicationSettings


def build_application() -> ApplicationContext:
    load_environment_file()
    settings = load_application_settings()
    return ApplicationContext(settings=settings)
