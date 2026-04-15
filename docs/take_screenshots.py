"""Take automated screenshots of the httpy TUI for documentation."""

import asyncio
from pathlib import Path

from httpy.core import set_basepath
from httpy.tui.app import HttpyApp


SCREENSHOT_DIR = Path("docs/screenshots")


async def take_screenshots() -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    set_basepath(Path("projects"))

    app = HttpyApp()
    async with app.run_test(size=(120, 36)) as pilot:
        # Main view with sidebar
        app.save_screenshot(str(SCREENSHOT_DIR / "main_view.svg"))

        # Click on a project in the tree to expand it
        tree = app.query_one("#project-tree")
        await pilot.pause()

        # Select a template
        from textual.widgets import Tree

        tree_widget = app.query_one("#project-tree", Tree)
        # Expand root and find template nodes
        for node in tree_widget.root.children:
            for child in node.children:
                for leaf in child.children:
                    if leaf.data and leaf.data[0] == "template":
                        tree_widget.select_node(leaf)
                        tree_widget.action_select_cursor()
                        await pilot.pause()
                        break
                if app.query_one("#template-editor").display:
                    break
            if app.query_one("#template-editor").display:
                break

        await pilot.pause()
        app.save_screenshot(str(SCREENSHOT_DIR / "template_editor.svg"))


if __name__ == "__main__":
    asyncio.run(take_screenshots())
