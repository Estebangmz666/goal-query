try:
    from src.app.bootstrap import build_application
except ModuleNotFoundError:
    from app.bootstrap import build_application


WELCOME_TEXT = """
========================================
              GoalQuery
 World Cup Management and Simulation App
========================================
""".strip()


def main() -> None:
    application = build_application()

    print(WELCOME_TEXT)
    print(f"Environment: {application.settings.app_env}")
    print(f"Debug mode: {application.settings.debug}")
    print("Base project configuration loaded successfully.")


if __name__ == "__main__":
    main()
