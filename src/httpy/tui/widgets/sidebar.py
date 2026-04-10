from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Static, Tree
from textual.widget import Widget

from httpy.core.environment import HttpyEnvironment
from httpy.core.project import HttpyProject
from httpy.core.template import HttpyRequestTemplate
from httpy.io import list_projects, load_project


class ProjectSidebar(Widget):
    class ProjectSelected(Message):
        def __init__(self, project: HttpyProject) -> None:
            super().__init__()
            self.project = project

    class TemplateSelected(Message):
        def __init__(
            self, template: HttpyRequestTemplate, project: HttpyProject
        ) -> None:
            super().__init__()
            self.template = template
            self.project = project

    class EnvironmentSelected(Message):
        def __init__(
            self, environment: HttpyEnvironment, project: HttpyProject
        ) -> None:
            super().__init__()
            self.environment = environment
            self.project = project

    def compose(self) -> ComposeResult:
        yield Static("Projects", classes="sidebar-title")
        yield Tree("Projects", id="project-tree")

    def on_mount(self) -> None:
        self.refresh_tree()

    def refresh_tree(self) -> None:
        tree = self.query_one("#project-tree", Tree)
        tree.clear()
        tree.root.expand()

        project_names = list_projects()
        for project_name in project_names:
            try:
                project = load_project(project_name, include_templates=True)
                project_node = tree.root.add(
                    f"📁 {project.name}", data=("project", project)
                )
                project_node.expand()

                env_group = project_node.add("🌐 Environments", data=("group", None))
                for env in project.environments:
                    env_group.add_leaf(
                        f"  {env.name}", data=("environment", env, project)
                    )

                tmpl_group = project_node.add("📋 Templates", data=("group", None))
                for tmpl in project.templates:
                    method_label = tmpl.method.upper()
                    tmpl_group.add_leaf(
                        f"  [{method_label}] {tmpl.name}",
                        data=("template", tmpl, project),
                    )
            except Exception:
                tree.root.add_leaf(f"⚠ {project_name} (error loading)")

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node_data = event.node.data
        if node_data is None:
            return

        match node_data:
            case ("project", project):
                self.post_message(self.ProjectSelected(project))
            case ("template", template, project):
                self.post_message(self.TemplateSelected(template, project))
            case ("environment", environment, project):
                self.post_message(self.EnvironmentSelected(environment, project))
