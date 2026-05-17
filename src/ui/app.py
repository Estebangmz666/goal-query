from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
import platform
import tkinter as tk
from tkinter import messagebox, ttk

try:
    from src.app.bootstrap import ApplicationContext
    from src.domain.enums.user_role import UserRole
    from src.domain.exceptions.authentication_error import AuthenticationError
    from src.dto.auth_models import AuthenticatedSessionDTO
    from src.dto.player_models import CreatePlayerDTO, UpdatePlayerDTO
    from src.dto.team_models import CreateTeamDTO, UpdateTeamDTO
    from src.ui.dialogs import FieldSpec, prompt_for_values
except ModuleNotFoundError:
    from app.bootstrap import ApplicationContext
    from domain.enums.user_role import UserRole
    from domain.exceptions.authentication_error import AuthenticationError
    from dto.auth_models import AuthenticatedSessionDTO
    from dto.player_models import CreatePlayerDTO, UpdatePlayerDTO
    from dto.team_models import CreateTeamDTO, UpdateTeamDTO
    from ui.dialogs import FieldSpec, prompt_for_values


class GoalQueryApp:
    def __init__(self, root: tk.Tk, context: ApplicationContext) -> None:
        self._root = root
        self._context = context
        self._session: AuthenticatedSessionDTO | None = None

        self._root.title(context.settings.app_name)
        self._root.geometry("1240x760")
        self._root.minsize(1100, 700)
        self._root.withdraw()

        self._style = ttk.Style()
        try:
            self._style.theme_use("clam")
        except tk.TclError:
            pass

        self._build_shell()

    def run(self) -> None:
        self._root.after(0, self._show_login)
        self._root.mainloop()

    def _build_shell(self) -> None:
        self._header = ttk.Frame(self._root, padding=12)
        self._header.pack(fill="x")

        self._title_label = ttk.Label(self._header, text=self._context.settings.app_name, font=("TkDefaultFont", 18, "bold"))
        self._title_label.pack(side="left")

        self._session_label = ttk.Label(self._header, text="No active session")
        self._session_label.pack(side="left", padx=18)

        self._logout_button = ttk.Button(self._header, text="Cerrar sesión", command=self._logout, state="disabled")
        self._logout_button.pack(side="right")

        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._dashboard_tab = ttk.Frame(self._notebook, padding=16)
        self._teams_tab = ttk.Frame(self._notebook, padding=12)
        self._players_tab = ttk.Frame(self._notebook, padding=12)
        self._queries_tab = ttk.Frame(self._notebook, padding=12)
        self._reports_tab = ttk.Frame(self._notebook, padding=12)
        self._users_tab = ttk.Frame(self._notebook, padding=12)

        self._notebook.add(self._dashboard_tab, text="Inicio")
        self._notebook.add(self._teams_tab, text="Equipos")
        self._notebook.add(self._players_tab, text="Jugadores")
        self._notebook.add(self._queries_tab, text="Consultas")
        self._notebook.add(self._reports_tab, text="Reportes")
        self._notebook.add(self._users_tab, text="Usuarios")

        self._build_dashboard_tab()
        self._build_teams_tab()
        self._build_players_tab()
        self._build_queries_tab()
        self._build_reports_tab()
        self._build_users_tab()

    def _show_login(self) -> None:
        login = LoginWindow(self._root)
        self._root.wait_window(login)

        if login.result is None:
            self._root.after(0, self._root.destroy)
            return

        try:
            session = self._context.services.auth_service.login(
                username=login.result["username"],
                password=login.result["password"],
                machine_name=platform.node() or None,
                application_name=self._context.settings.app_name,
            )
        except AuthenticationError as error:
            messagebox.showerror("Login failed", str(error))
            self._root.after(0, self._show_login)
            return
        except Exception as error:
            messagebox.showerror("Unexpected error", str(error))
            self._root.after(0, self._show_login)
            return

        self._session = session
        self._session_label.config(text=f"{session.full_name} · {session.role.value}")
        self._logout_button.config(state="normal")
        self._root.deiconify()
        self._refresh_all()
        self._apply_role_visibility()

    def _build_dashboard_tab(self) -> None:
        frame = ttk.Frame(self._dashboard_tab)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="GoalQuery desktop shell", font=("TkDefaultFont", 22, "bold")).pack(anchor="w", pady=(0, 12))
        ttk.Label(
            frame,
            text=(
                "Use this interface to manage teams and players, run the mandatory queries, "
                "and inspect academic reports without touching SQL from the UI."
            ),
            wraplength=860,
            justify="left",
        ).pack(anchor="w")

        self._dashboard_status = ttk.Label(frame, text="Log in to start working with the tournament data.")
        self._dashboard_status.pack(anchor="w", pady=(16, 0))

    def _build_teams_tab(self) -> None:
        self._teams_table = self._build_entity_tab(
            self._teams_tab,
            columns=("id", "name", "fifa_code", "country_id", "confederation_id", "team_weight", "market_value", "group_id"),
            headings=("ID", "Nombre", "FIFA", "País", "Confederación", "Peso", "Valor", "Grupo"),
        )

        button_frame = ttk.Frame(self._teams_tab)
        button_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(button_frame, text="Actualizar", command=self._refresh_teams).pack(side="left")
        ttk.Button(button_frame, text="Nuevo", command=self._create_team).pack(side="left", padx=6)
        ttk.Button(button_frame, text="Editar", command=self._edit_team).pack(side="left", padx=6)
        ttk.Button(button_frame, text="Eliminar", command=self._delete_team).pack(side="left", padx=6)

    def _build_players_tab(self) -> None:
        self._players_table = self._build_entity_tab(
            self._players_tab,
            columns=("id", "team_id", "first_name", "last_name", "position", "shirt_number", "date_of_birth", "height_cm", "weight_kg", "market_value"),
            headings=("ID", "Equipo", "Nombre", "Apellido", "Posición", "Dorsal", "Nacimiento", "Estatura", "Peso", "Valor"),
        )

        button_frame = ttk.Frame(self._players_tab)
        button_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(button_frame, text="Actualizar", command=self._refresh_players).pack(side="left")
        ttk.Button(button_frame, text="Nuevo", command=self._create_player).pack(side="left", padx=6)
        ttk.Button(button_frame, text="Editar", command=self._edit_player).pack(side="left", padx=6)
        ttk.Button(button_frame, text="Eliminar", command=self._delete_player).pack(side="left", padx=6)

    def _build_queries_tab(self) -> None:
        self._queries_output = self._build_result_panel(self._queries_tab)

        button_frame = ttk.Frame(self._queries_tab)
        button_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(button_frame, text="Jugador más costoso por confederación", command=self._run_query_most_expensive_player).pack(anchor="w")
        ttk.Button(button_frame, text="Partidos por estadio", command=self._run_query_matches_by_stadium).pack(anchor="w", pady=4)
        ttk.Button(button_frame, text="Equipo más costoso por país anfitrión", command=self._run_query_most_expensive_team).pack(anchor="w")
        ttk.Button(button_frame, text="Jugadores menores de 21 por equipo", command=self._run_query_under_twenty_one).pack(anchor="w", pady=4)

    def _build_reports_tab(self) -> None:
        self._reports_output = self._build_result_panel(self._reports_tab)

        button_frame = ttk.Frame(self._reports_tab)
        button_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(button_frame, text="Sesiones por fecha y hora", command=self._run_report_sessions).pack(anchor="w")
        ttk.Button(button_frame, text="Jugadores filtrados", command=self._run_report_players).pack(anchor="w", pady=4)
        ttk.Button(button_frame, text="Valor total por confederación", command=self._run_report_team_values).pack(anchor="w")
        ttk.Button(button_frame, text="Países por país anfitrión", command=self._run_report_countries).pack(anchor="w", pady=4)

    def _build_users_tab(self) -> None:
        self._users_body = ttk.Frame(self._users_tab)
        self._users_body.pack(fill="both", expand=True)

        ttk.Label(
            self._users_body,
            text="User management is available for administrators only.",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))
        ttk.Button(self._users_body, text="Create user", command=self._create_user).pack(anchor="w")

    def _build_entity_tab(self, parent: ttk.Frame, columns: tuple[str, ...], headings: tuple[str, ...]) -> ttk.Treeview:
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        for column, heading in zip(columns, headings, strict=True):
            tree.heading(column, text=heading)
            tree.column(column, width=120, anchor="w")

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    def _build_result_panel(self, parent: ttk.Frame) -> ttk.Treeview:
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, show="headings", height=18)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tree

    def _apply_role_visibility(self) -> None:
        if self._session is None:
            return

        role = self._session.role
        can_manage = role in {UserRole.ADMINISTRATOR, UserRole.TRADITIONAL_USER}
        can_reports = role in {UserRole.ADMINISTRATOR, UserRole.TRADITIONAL_USER}

        self._set_tab_state(self._teams_tab, can_manage)
        self._set_tab_state(self._players_tab, can_manage)
        self._set_tab_state(self._reports_tab, can_reports)
        self._set_tab_state(self._users_tab, role == UserRole.ADMINISTRATOR)

        if role == UserRole.SPORADIC_USER:
            self._dashboard_status.config(text="Sporadic users can execute queries only.")
        elif role == UserRole.TRADITIONAL_USER:
            self._dashboard_status.config(text="Traditional users can manage data, execute queries and generate reports.")
        else:
            self._dashboard_status.config(text="Administrator access enabled.")

    def _set_tab_state(self, tab: ttk.Frame, enabled: bool) -> None:
        self._notebook.tab(tab, state="normal" if enabled else "hidden")

    def _refresh_all(self) -> None:
        self._refresh_teams()
        self._refresh_players()
        self._clear_result_tree(self._queries_output)
        self._clear_result_tree(self._reports_output)

    def _refresh_teams(self) -> None:
        self._load_tree_rows(self._teams_table, [asdict(team) for team in self._context.services.team_service.get_all_teams()])

    def _refresh_players(self) -> None:
        self._load_tree_rows(self._players_table, [asdict(player) for player in self._context.services.player_service.get_all_players()])

    def _create_team(self) -> None:
        if self._session is None:
            return

        values = prompt_for_values(
            self._root,
            "Nuevo equipo",
            [
                FieldSpec("name", "Nombre"),
                FieldSpec("fifa_code", "Código FIFA"),
                FieldSpec("country_id", "ID país", kind="int"),
                FieldSpec("confederation_id", "ID confederación", kind="int"),
                FieldSpec("team_weight", "Peso del equipo", kind="float"),
                FieldSpec("market_value", "Valor de mercado", kind="float"),
                FieldSpec("group_id", "ID grupo", kind="int", required=False),
            ],
        )
        if values is None:
            return

        try:
            self._context.services.team_service.create_team(self._session.role, CreateTeamDTO(**values))
            self._refresh_teams()
            messagebox.showinfo("Éxito", "Equipo creado correctamente.")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _edit_team(self) -> None:
        if self._session is None:
            return

        selected = self._get_selected_row(self._teams_table)
        if selected is None:
            return

        values = prompt_for_values(
            self._root,
            "Editar equipo",
            [
                FieldSpec("name", "Nombre"),
                FieldSpec("fifa_code", "Código FIFA"),
                FieldSpec("team_weight", "Peso del equipo", kind="float"),
                FieldSpec("market_value", "Valor de mercado", kind="float"),
                FieldSpec("group_id", "ID grupo", kind="int", required=False),
            ],
            initial_values=selected,
        )
        if values is None:
            return

        try:
            self._context.services.team_service.update_team(self._session.role, int(selected["id"]), UpdateTeamDTO(**values))
            self._refresh_teams()
            messagebox.showinfo("Éxito", "Equipo actualizado correctamente.")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _delete_team(self) -> None:
        if self._session is None:
            return

        selected = self._get_selected_row(self._teams_table)
        if selected is None:
            return

        if not messagebox.askyesno("Confirmación", f"¿Eliminar el equipo {selected['name']}?"):
            return

        try:
            self._context.services.team_service.delete_team(self._session.role, int(selected["id"]))
            self._refresh_teams()
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _create_player(self) -> None:
        if self._session is None:
            return

        values = prompt_for_values(
            self._root,
            "Nuevo jugador",
            [
                FieldSpec("team_id", "ID equipo", kind="int"),
                FieldSpec("first_name", "Nombre"),
                FieldSpec("last_name", "Apellido"),
                FieldSpec("position", "Posición"),
                FieldSpec("shirt_number", "Dorsal", kind="int"),
                FieldSpec("date_of_birth", "Fecha de nacimiento (YYYY-MM-DD)", kind="date"),
                FieldSpec("height_cm", "Estatura (cm)", kind="float"),
                FieldSpec("weight_kg", "Peso (kg)", kind="float"),
                FieldSpec("market_value", "Valor de mercado", kind="float"),
            ],
        )
        if values is None:
            return

        try:
            self._context.services.player_service.create_player(self._session.role, CreatePlayerDTO(**values))
            self._refresh_players()
            messagebox.showinfo("Éxito", "Jugador creado correctamente.")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _edit_player(self) -> None:
        if self._session is None:
            return

        selected = self._get_selected_row(self._players_table)
        if selected is None:
            return

        values = prompt_for_values(
            self._root,
            "Editar jugador",
            [
                FieldSpec("position", "Posición"),
                FieldSpec("shirt_number", "Dorsal", kind="int"),
                FieldSpec("height_cm", "Estatura (cm)", kind="float"),
                FieldSpec("weight_kg", "Peso (kg)", kind="float"),
                FieldSpec("market_value", "Valor de mercado", kind="float"),
            ],
            initial_values=selected,
        )
        if values is None:
            return

        try:
            self._context.services.player_service.update_player(self._session.role, int(selected["id"]), UpdatePlayerDTO(**values))
            self._refresh_players()
            messagebox.showinfo("Éxito", "Jugador actualizado correctamente.")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _delete_player(self) -> None:
        if self._session is None:
            return

        selected = self._get_selected_row(self._players_table)
        if selected is None:
            return

        if not messagebox.askyesno("Confirmación", f"¿Eliminar al jugador {selected['first_name']} {selected['last_name']}?"):
            return

        try:
            self._context.services.player_service.delete_player(self._session.role, int(selected["id"]))
            self._refresh_players()
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _run_query_most_expensive_player(self) -> None:
        rows = [asdict(row) for row in self._context.services.query_service.get_most_expensive_player_by_confederation()]
        self._show_result_rows(rows, self._queries_output)

    def _run_query_matches_by_stadium(self) -> None:
        values = prompt_for_values(self._root, "Partidos por estadio", [FieldSpec("stadium_id", "ID estadio", kind="int")])
        if values is None:
            return

        rows = [asdict(row) for row in self._context.services.query_service.get_matches_by_stadium(int(values["stadium_id"]))]
        self._show_result_rows(rows, self._queries_output)

    def _run_query_most_expensive_team(self) -> None:
        rows = [asdict(row) for row in self._context.services.query_service.get_most_expensive_team_by_host_country()]
        self._show_result_rows(rows, self._queries_output)

    def _run_query_under_twenty_one(self) -> None:
        values = prompt_for_values(self._root, "Jugadores menores de 21", [FieldSpec("reference_date", "Fecha de referencia (YYYY-MM-DD)", kind="date")])
        if values is None:
            return

        rows = [asdict(row) for row in self._context.services.query_service.get_under_twenty_one_players_by_team(values["reference_date"])]
        self._show_result_rows(rows, self._queries_output)

    def _run_report_sessions(self) -> None:
        if self._session is None:
            return

        values = prompt_for_values(
            self._root,
            "Sesiones por rango",
            [
                FieldSpec("start_datetime", "Inicio (YYYY-MM-DD HH:MM)", kind="datetime"),
                FieldSpec("end_datetime", "Fin (YYYY-MM-DD HH:MM)", kind="datetime"),
            ],
        )
        if values is None:
            return

        rows = [
            asdict(row)
            for row in self._context.services.report_service.get_user_sessions_by_datetime_range(
                self._session.role,
                values["start_datetime"],
                values["end_datetime"],
            )
        ]
        self._show_result_rows(rows, self._reports_output)

    def _run_report_players(self) -> None:
        if self._session is None:
            return

        values = prompt_for_values(
            self._root,
            "Jugadores filtrados",
            [
                FieldSpec("minimum_weight_kg", "Peso mínimo", kind="float"),
                FieldSpec("maximum_weight_kg", "Peso máximo", kind="float"),
                FieldSpec("minimum_height_cm", "Estatura mínima", kind="float"),
                FieldSpec("maximum_height_cm", "Estatura máxima", kind="float"),
                FieldSpec("team_name", "Nombre del equipo"),
            ],
        )
        if values is None:
            return

        rows = [
            asdict(row)
            for row in self._context.services.report_service.get_players_by_filters(
                self._session.role,
                values["minimum_weight_kg"],
                values["maximum_weight_kg"],
                values["minimum_height_cm"],
                values["maximum_height_cm"],
                values["team_name"],
            )
        ]
        self._show_result_rows(rows, self._reports_output)

    def _run_report_team_values(self) -> None:
        if self._session is None:
            return

        values = prompt_for_values(self._root, "Valor total por confederación", [FieldSpec("confederation_code", "Código de confederación")])
        if values is None:
            return

        rows = [
            asdict(row)
            for row in self._context.services.report_service.get_total_player_value_by_confederation(
                self._session.role,
                values["confederation_code"],
            )
        ]
        self._show_result_rows(rows, self._reports_output)

    def _run_report_countries(self) -> None:
        if self._session is None:
            return

        rows = [asdict(row) for row in self._context.services.report_service.get_countries_playing_by_host_country(self._session.role)]
        self._show_result_rows(rows, self._reports_output)

    def _create_user(self) -> None:
        if self._session is None or self._session.role != UserRole.ADMINISTRATOR:
            messagebox.showwarning("Acceso denegado", "Solo el administrador puede crear usuarios.")
            return

        values = prompt_for_values(
            self._root,
            "Nuevo usuario",
            [
                FieldSpec("username", "Usuario"),
                FieldSpec("full_name", "Nombre completo"),
                FieldSpec("raw_password", "Contraseña", kind="password"),
                FieldSpec("role", "Rol", choices=(UserRole.ADMINISTRATOR.value, UserRole.TRADITIONAL_USER.value, UserRole.SPORADIC_USER.value)),
            ],
        )
        if values is None:
            return

        try:
            created = self._context.services.user_service.create_user(
                self._session.role,
                values["username"],
                values["full_name"],
                values["raw_password"],
                UserRole(values["role"]),
            )
            messagebox.showinfo("Éxito", f"Usuario {created.username} creado correctamente.")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _show_result_rows(self, rows: list[dict[str, object]], tree: ttk.Treeview) -> None:
        self._clear_result_tree(tree)
        if not rows:
            messagebox.showinfo("Sin resultados", "La consulta no devolvió filas.")
            return

        columns = list(rows[0].keys())
        tree["columns"] = columns
        for column in columns:
            tree.heading(column, text=column.replace("_", " ").title())
            tree.column(column, width=160, anchor="w")

        for row in rows:
            tree.insert("", "end", values=[self._format_value(row[column]) for column in columns])

    def _load_tree_rows(self, tree: ttk.Treeview, rows: list[dict[str, object]]) -> None:
        self._clear_result_tree(tree)
        if not rows:
            return

        columns = list(rows[0].keys())
        tree["columns"] = columns
        for column in columns:
            tree.heading(column, text=column.replace("_", " ").title())
            tree.column(column, width=130, anchor="w")

        for row in rows:
            tree.insert("", "end", values=[self._format_value(row[column]) for column in columns])

    @staticmethod
    def _clear_result_tree(tree: ttk.Treeview) -> None:
        tree.delete(*tree.get_children())

    @staticmethod
    def _format_value(value: object) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.isoformat(sep=" ")
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return f"{value:.2f}"
        return str(value)

    def _get_selected_row(self, tree: ttk.Treeview) -> dict[str, object] | None:
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selección requerida", "Selecciona una fila primero.")
            return None

        item = tree.item(selected[0])
        columns = list(tree["columns"])
        return {column: item["values"][index] for index, column in enumerate(columns)}

    def _logout(self) -> None:
        if self._session is not None:
            try:
                self._context.services.auth_service.logout(self._session.audit_log_id)
            except Exception as error:
                messagebox.showerror("Logout error", str(error))
            finally:
                self._session = None

        self._root.destroy()


class LoginWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk) -> None:
        super().__init__(parent)
        self.result: dict[str, str] | None = None
        self.title("Inicio de sesión")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Usuario").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Label(frame, text="Contraseña").grid(row=1, column=0, sticky="w", pady=4)

        self._username = tk.StringVar()
        self._password = tk.StringVar()

        ttk.Entry(frame, textvariable=self._username).grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Entry(frame, textvariable=self._password, show="*").grid(row=1, column=1, sticky="ew", pady=4)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(button_frame, text="Entrar", command=self._submit).pack(side="right")
        ttk.Button(button_frame, text="Cancelar", command=self._cancel).pack(side="right", padx=6)

        frame.columnconfigure(1, weight=1)
        self.bind("<Return>", lambda _: self._submit())
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.update_idletasks()
        self._center()
        self.deiconify()
        self.lift()
        self.focus_force()
        self.grab_set()

    def _submit(self) -> None:
        self.result = {"username": self._username.get().strip(), "password": self._password.get()}
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()

    def _center(self) -> None:
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = max((self.winfo_screenwidth() // 2) - (width // 2), 40)
        y = max((self.winfo_screenheight() // 2) - (height // 2), 40)
        self.geometry(f"+{x}+{y}")