import logging
from pathlib import Path

import dearpygui.dearpygui as dpg
from screeninfo import get_monitors

import Application
import GUI
from themes import create_gruvbox_dark_theme

logger = logging.getLogger("Core.Main")

def start_editing(path: Path):
    main_image_ratio = 0.7
    monitors = get_monitors()
    logger.debug(monitors)
    for monitor in monitors:
        image_width = int(monitor.width * main_image_ratio)
        main_image_dimensions = (image_width, int(image_width * 2 / 3))
        thumnail_dimensions = (200, 200)
        image_x, image_y = main_image_dimensions
        window_dimensions = (image_x + 40, image_y + 100)
        logger.debug("Making ImageManager")
        image_manager = Application.ImageManager.from_path(
            path, main_image_dimensions, thumnail_dimensions
        )
        logger.debug("Made ImageManager")
        GUI.ImageWindow(
            roll=path.name,
            image_manager=image_manager,
            main_image_dimensions=main_image_dimensions,
            thumnail_dimensions=thumnail_dimensions,
            window_dimensions=window_dimensions,
        )


def load_image_folder(sender, app_data, user_data):
    path = Path(app_data["file_path_name"])
    start_editing(path)

def main():
    dpg.create_context()
    create_gruvbox_dark_theme()
    dpg.create_viewport(title="Gredit")
    core_logger = logging.getLogger("Core")
    gui_logger = logging.getLogger("GUI")
    core_logger.setLevel(logging.DEBUG)
    gui_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[{threadName}][{asctime}] [{levelname:<8}] {name}: {message}",
        "%H:%M:%S",
        style="{",
    )

    with dpg.colormap_registry():
        dpg.add_colormap(
            [[0, 255, 255], [255, 0, 0]],
            False,
            tag="red",
        )

        dpg.add_colormap(
            [[255, 0, 255], [0, 255, 0]],
            False,
            tag="green",
        )

        dpg.add_colormap(
            [[255, 255, 0], [0, 0, 255]],
            False,
            tag="blue",
        )

    with dpg.window(tag="Primary Window"):
        dpg.add_file_dialog(
            directory_selector=True,
            show=False,
            tag="roll_folder_dialog",
            callback=load_image_folder,
            height=400,
        )


        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(
                    label="Load Folder",
                    callback=lambda: dpg.show_item("roll_folder_dialog"),
                )
            with dpg.menu(label="Tools"):
                dpg.add_menu_item(
                    label="Show Performance Metrics", callback=dpg.show_metrics
                )

    log = GUI.Logger()
    log.setFormatter(formatter)
    core_logger.addHandler(log)
    gui_logger.addHandler(log)

    dpg.setup_dearpygui()
    dpg.set_primary_window("Primary Window", True)
    dpg.set_viewport_vsync(False)
    dpg.show_viewport(maximized=True)

    import sys

    sys.stderr = log

    if sys.platform == "win32":
        from ctypes import windll
        import pywinstyles

        hwnd = windll.user32.FindWindowW(None, "Gredit")
        pywinstyles.change_header_color(hwnd, color="black")

    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
