import tkinter as tk

try:
    from src.app.bootstrap import build_application
    from src.ui.app import GoalQueryApp
except ModuleNotFoundError:
    from app.bootstrap import build_application
    from ui.app import GoalQueryApp


WELCOME_TEXT = """
========================================
              GoalQuery
 World Cup Management and Simulation App
========================================
""".strip()


def main() -> None:
    print("inicializando GoalQuery...")
    application = build_application()
    print("aplicacion build completo")
    root = tk.Tk()
    print("creando GUIGoalQueryApp...")
    app = GoalQueryApp(root, application)

    print(WELCOME_TEXT)
    print(f"Environment: {application.settings.app_env}")
    print(f"Debug mode: {application.settings.debug}")
    print("Base project configuration loaded successfully.")
    app.run()


if __name__ == "__main__":
    main()
