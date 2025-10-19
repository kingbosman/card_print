"""
Page builder module.

Handles creation of individual pages with cards and cut marks.
"""

from PIL import Image, ImageDraw
import os


def create_single_page(
    image_files,
    page_num,
    total_pages,
    config,
    card_width_px,
    card_height_px,
    spacing_px,
    paper_width_px,
    paper_height_px,
    start_x,
    start_y,
    MM_TO_PIXELS,
):
    """
    Creates a single page with cards based on config settings.

    Args:
        image_files: List of image file paths for this page
        page_num: Current page number
        total_pages: Total number of pages
        config: Configuration dictionary
        card_width_px: Card width in pixels
        card_height_px: Card height in pixels
        spacing_px: Spacing between cards in pixels
        paper_width_px: Paper width in pixels
        paper_height_px: Paper height in pixels
        start_x: Starting X position for grid
        start_y: Starting Y position for grid
        MM_TO_PIXELS: Conversion factor from mm to pixels

    Returns:
        PIL.Image: Generated page image
    """
    # Create blank canvas (white background)
    canvas = Image.new("RGB", (paper_width_px, paper_height_px), "white")
    draw = ImageDraw.Draw(canvas)

    grid_cols = config["GRID_COLS"]
    grid_rows = config["GRID_ROWS"]

    print(f"\nPage {page_num}/{total_pages}:")
    print(f"  Placing {len(image_files)} cards...")

    # Place cards in grid
    _place_cards(
        canvas,
        draw,
        image_files,
        grid_rows,
        grid_cols,
        start_x,
        start_y,
        card_width_px,
        card_height_px,
        spacing_px,
    )

    # Add corner marks
    _add_corner_marks(
        draw,
        image_files,
        config,
        grid_rows,
        grid_cols,
        start_x,
        start_y,
        card_width_px,
        card_height_px,
        spacing_px,
        MM_TO_PIXELS,
    )

    # Add guide lines if enabled
    _add_guide_lines(
        draw,
        config,
        grid_rows,
        grid_cols,
        start_x,
        start_y,
        card_width_px,
        card_height_px,
        spacing_px,
    )

    return canvas


def _place_cards(
    canvas,
    draw,
    image_files,
    grid_rows,
    grid_cols,
    start_x,
    start_y,
    card_width_px,
    card_height_px,
    spacing_px,
):
    """Place card images on the canvas in a grid layout."""
    card_index = 0
    for row in range(grid_rows):
        for col in range(grid_cols):
            if card_index >= len(image_files):
                break

            # Calculate position
            x = start_x + col * (card_width_px + spacing_px)
            y = start_y + row * (card_height_px + spacing_px)

            # Load and resize card image
            try:
                card_img = Image.open(image_files[card_index])

                # Resize to exact card dimensions while maintaining quality
                card_img = card_img.resize(
                    (card_width_px, card_height_px), Image.LANCZOS
                )

                # Paste card onto canvas
                canvas.paste(card_img, (x, y))

                print(
                    f"    [{card_index + 1}/{len(image_files)}] {os.path.basename(image_files[card_index])}"
                )

            except Exception as e:
                print(
                    f"    ❌ Error loading {os.path.basename(image_files[card_index])}: {e}"
                )

            card_index += 1

        if card_index >= len(image_files):
            break


def _add_corner_marks(
    draw,
    image_files,
    config,
    grid_rows,
    grid_cols,
    start_x,
    start_y,
    card_width_px,
    card_height_px,
    spacing_px,
    MM_TO_PIXELS,
):
    """Add corner cut marks at each card corner."""
    mark_length = int(config["MARK_LENGTH_MM"] * MM_TO_PIXELS)
    corner_color = (
        config["MARK_COLOR_R"],
        config["MARK_COLOR_G"],
        config["MARK_COLOR_B"],
    )
    mark_width = config["MARK_WIDTH_PX"]

    print(f"  Adding corner cut marks...")

    # Draw corner marks at each of the 4 corners of every card
    card_index = 0
    for row in range(grid_rows):
        for col in range(grid_cols):
            if card_index >= len(image_files):
                break

            # Calculate card position
            x = start_x + col * (card_width_px + spacing_px)
            y = start_y + row * (card_height_px + spacing_px)

            # Draw crosses at all 4 corners of this card
            corners = [
                (x, y),  # Top-left
                (x + card_width_px, y),  # Top-right
                (x, y + card_height_px),  # Bottom-left
                (x + card_width_px, y + card_height_px),  # Bottom-right
            ]

            for corner_x, corner_y in corners:
                # Draw cross: horizontal and vertical lines
                # Horizontal line (left and right from corner)
                draw.line(
                    [
                        (corner_x - mark_length, corner_y),
                        (corner_x + mark_length, corner_y),
                    ],
                    fill=corner_color,
                    width=mark_width,
                )

                # Vertical line (up and down from corner)
                draw.line(
                    [
                        (corner_x, corner_y - mark_length),
                        (corner_x, corner_y + mark_length),
                    ],
                    fill=corner_color,
                    width=mark_width,
                )

            card_index += 1

        if card_index >= len(image_files):
            break


def _add_guide_lines(
    draw,
    config,
    grid_rows,
    grid_cols,
    start_x,
    start_y,
    card_width_px,
    card_height_px,
    spacing_px,
):
    """Add guide lines around the card grid if enabled in config."""
    if not config.get("GUIDE_LINE_ENABLED", True):
        return

    guide_color = (
        config["GUIDE_LINE_COLOR_R"],
        config["GUIDE_LINE_COLOR_G"],
        config["GUIDE_LINE_COLOR_B"],
    )
    guide_width = config["GUIDE_LINE_WIDTH_PX"]

    total_grid_width = (card_width_px * grid_cols) + (spacing_px * (grid_cols - 1))
    total_grid_height = (card_height_px * grid_rows) + (spacing_px * (grid_rows - 1))

    # Vertical guide lines
    for col in range(grid_cols + 1):
        x = start_x + col * (card_width_px + spacing_px)
        draw.line(
            [(x, start_y), (x, start_y + total_grid_height)],
            fill=guide_color,
            width=guide_width,
        )

    # Horizontal guide lines
    for row in range(grid_rows + 1):
        y = start_y + row * (card_height_px + spacing_px)
        draw.line(
            [(start_x, y), (start_x + total_grid_width, y)],
            fill=guide_color,
            width=guide_width,
        )
