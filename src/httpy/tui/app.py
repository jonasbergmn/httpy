from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header

from httpy.tui.widgets.sidebar import ProjectSidebar
from httpy.tui.widgets.template_editor import TemplateEditor
from httpy.tui.widgets.environment_editor import EnvironmentEditor
from httpy.tui.widgets.response_viewer import ResponseViewer
from httpy.tui.screens.new_project import NewProjectScreen
from httpy.tui.screens.new_template import NewTemplateScreen
from httpy.tui.screens.new_environment import NewEnvironmentScreen

from httpy.core.environment import HttpyEnvironment
from httpy.core.template import HttpyRequestTemplate
from httpy.core.project import HttpyProject
from httpy.core.response import HttpyResponse


class HttpyApp(App):
    TITLE = "httpy"
    SUB_TITLE = "HTTP Request Collection Manager"
    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("n", "new_project", "New Project"),
        Binding("t", "new_template", "New Template"),
        Binding("e", "new_environment", "New Environment"),
    ]

    current_project: HttpyProject | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            yield ProjectSidebar(id="sidebar")
            with Vertical(id="main-panel"):
                yield TemplateEditor(id="template-editor")
                yield EnvironmentEditor(id="environment-editor")
                yield ResponseViewer(id="response-viewer")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#template-editor", TemplateEditor).display = False
        self.query_one("#environment-editor", EnvironmentEditor).display = False
        self.query_one("#response-viewer", ResponseViewer).display = False

    def on_project_sidebar_project_selected(
        self, message: ProjectSidebar.ProjectSelected
    ) -> None:
        self.current_project = message.project
        self._hide_all_panels()

    def on_project_sidebar_template_selected(
        self, message: ProjectSidebar.TemplateSelected
    ) -> None:
        self.current_project = message.project
        self._hide_all_panels()
        editor = self.query_one("#template-editor", TemplateEditor)
        editor.load_template(message.template, message.project)
        editor.display = True

    def on_project_sidebar_environment_selected(
        self, message: ProjectSidebar.EnvironmentSelected
    ) -> None:
        self.current_project = message.project
        self._hide_all_panels()
        editor = self.query_one("#environment-editor", EnvironmentEditor)
        editor.load_environment(message.environment, message.project)
        editor.display = True

    def on_template_editor_request_sent(
        self, message: TemplateEditor.RequestSent
    ) -> None:
        viewer = self.query_one("#response-viewer", ResponseViewer)
        viewer.show_response(message.response)
        viewer.display = True

    def on_template_editor_template_saved(
        self, message: TemplateEditor.TemplateSaved
    ) -> None:
        sidebar = self.query_one("#sidebar", ProjectSidebar)
        sidebar.refresh_tree()

    def on_environment_editor_environment_saved(
        self, message: EnvironmentEditor.EnvironmentSaved
    ) -> None:
        sidebar = self.query_one("#sidebar", ProjectSidebar)
        sidebar.refresh_tree()

    def action_new_project(self) -> None:
        def on_project_created(project: HttpyProject | None) -> None:
            if project is not None:
                sidebar = self.query_one("#sidebar", ProjectSidebar)
                sidebar.refresh_tree()

        self.push_screen(NewProjectScreen(), callback=on_project_created)

    def action_new_template(self) -> None:
        if self.current_project is None:
            self.notify("Select a project first", severity="warning")
            return

        def on_template_created(template: HttpyRequestTemplate | None) -> None:
            if template is not None:
                sidebar = self.query_one("#sidebar", ProjectSidebar)
                sidebar.refresh_tree()

        self.push_screen(
            NewTemplateScreen(self.current_project), callback=on_template_created
        )

    def action_new_environment(self) -> None:
        if self.current_project is None:
            self.notify("Select a project first", severity="warning")
            return

        def on_environment_created(environment: HttpyEnvironment | None) -> None:
            if environment is not None:
                sidebar = self.query_one("#sidebar", ProjectSidebar)
                sidebar.refresh_tree()

        self.push_screen(
            NewEnvironmentScreen(self.current_project), callback=on_environment_created
        )

    def _hide_all_panels(self) -> None:
        self.query_one("#template-editor", TemplateEditor).display = False
        self.query_one("#environment-editor", EnvironmentEditor).display = False
        self.query_one("#response-viewer", ResponseViewer).display = False
