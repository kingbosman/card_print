"""
Sheet generator module.

Main logic for generating complete card sheets with multiple pages.
"""

import os
import sys
import time
from .config_loader import load_config
from .page_builder import create_single_page


def generate_sheets(config_file="config/current.conf"):
    """
    Creates sheets with cards arranged in a grid based on config settings.
    Supports unlimited cards - creates multiple PNG files or multi-page PDF.
    Cards have corner marks for precise cutting.

    Args:
        config_file: Path to configuration file (default: config/current.conf)
    """

    # Load configuration
    config = load_config(config_file)

    # Paper dimensions - apply orientation
    base_width_mm = config["PAPER_WIDTH_MM"]
    base_height_mm = config["PAPER_HEIGHT_MM"]
    orientation = config.get("PAPER_ORIENTATION", "landscape").lower()

    # Swap dimensions if portrait orientation
    if orientation == "portrait":
        # Swap to portrait (taller than wide)
        if base_width_mm > base_height_mm:
            paper_width_mm = base_height_mm
            paper_height_mm = base_width_mm
        else:
            paper_width_mm = base_width_mm
            paper_height_mm = base_height_mm
    else:  # landscape
        # Swap to landscape (wider than tall)
        if base_width_mm < base_height_mm:
            paper_width_mm = base_height_mm
            paper_height_mm = base_width_mm
        else:
            paper_width_mm = base_width_mm
            paper_height_mm = base_height_mm

    dpi = config["DPI"]

    # Convert mm to pixels
    mm_to_pixels = dpi / 25.4
    paper_width_px = int(paper_width_mm * mm_to_pixels)
    paper_height_px = int(paper_height_mm * mm_to_pixels)

    # Card dimensions
    card_width_mm = config["CARD_WIDTH_MM"]
    card_height_mm = config["CARD_HEIGHT_MM"]
    card_width_px = int(card_width_mm * mm_to_pixels)
    card_height_px = int(card_height_mm * mm_to_pixels)

    # Gap between cards
    gap_mm = config["GAP_MM"]
    spacing_px = int(gap_mm * mm_to_pixels)

    # Input/Output
    image_folder = config["CARD_IMAGES_FOLDER"]
    output_filename = config["OUTPUT_FILE"]

    # Create outputs directory if it doesn't exist
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    # Add timestamp prefix to output filename
    timestamp = int(time.time())
    output_filename = f"{timestamp}_{output_filename}"
    output_path = os.path.join(output_dir, output_filename)

    # Get all image files from folder
    image_files = _get_image_files(image_folder)

    if len(image_files) == 0:
        print(f"❌ Error: No images found in '{image_folder}'")
        print(f"   Supported formats: PNG, JPG, JPEG, WEBP, BMP")
        return

    # Grid configuration
    grid_cols = config["GRID_COLS"]
    grid_rows = config["GRID_ROWS"]
    cards_per_page = grid_cols * grid_rows

    # Validate that the grid fits on the page
    _validate_grid_fits(
        paper_width_mm,
        paper_height_mm,
        card_width_mm,
        card_height_mm,
        gap_mm,
        grid_cols,
        grid_rows,
        orientation,
    )

    # Calculate how many pages we need
    total_pages = (len(image_files) + cards_per_page - 1) // cards_per_page

    # Print summary
    _print_summary(
        image_files,
        paper_width_mm,
        paper_height_mm,
        card_width_mm,
        card_height_mm,
        gap_mm,
        dpi,
        cards_per_page,
        grid_cols,
        grid_rows,
        total_pages,
        orientation,
    )

    # Calculate starting position to center the grid
    total_grid_width = (card_width_px * grid_cols) + (spacing_px * (grid_cols - 1))
    total_grid_height = (card_height_px * grid_rows) + (spacing_px * (grid_rows - 1))

    start_x = (paper_width_px - total_grid_width) // 2
    start_y = (paper_height_px - total_grid_height) // 2

    # Split cards into pages
    pages = []
    for page_num in range(total_pages):
        start_idx = page_num * cards_per_page
        end_idx = min(start_idx + cards_per_page, len(image_files))
        page_cards = image_files[start_idx:end_idx]

        canvas = create_single_page(
            page_cards,
            page_num + 1,
            total_pages,
            config,
            card_width_px,
            card_height_px,
            spacing_px,
            paper_width_px,
            paper_height_px,
            start_x,
            start_y,
            mm_to_pixels,
        )
        pages.append(canvas)

    # Save the result(s)
    _save_pages(pages, output_path, output_dir, dpi)

    # Print final summary
    _print_final_summary(
        config,
        paper_width_mm,
        paper_height_mm,
        grid_cols,
        grid_rows,
        cards_per_page,
        dpi,
        paper_width_px,
        paper_height_px,
        image_files,
        total_pages,
        card_width_mm,
        card_height_mm,
        card_width_px,
        card_height_px,
        gap_mm,
        start_x,
        start_y,
        mm_to_pixels,
        orientation,
    )


def _get_image_files(image_folder):
    """Get all image files from folder."""
    image_files = []
    for file in sorted(os.listdir(image_folder)):
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp")):
            image_files.append(os.path.join(image_folder, file))
    return image_files


def _validate_grid_fits(
    paper_width_mm,
    paper_height_mm,
    card_width_mm,
    card_height_mm,
    gap_mm,
    grid_cols,
    grid_rows,
    orientation,
):
    """
    Validate that the card grid fits on the paper.

    Exits with error message if the grid doesn't fit.
    """
    # Calculate total space needed
    total_width_needed = (card_width_mm * grid_cols) + (gap_mm * (grid_cols - 1))
    total_height_needed = (card_height_mm * grid_rows) + (gap_mm * (grid_rows - 1))

    # Check if it fits
    width_fits = total_width_needed <= paper_width_mm
    height_fits = total_height_needed <= paper_height_mm

    if not width_fits or not height_fits:
        print(f"\n{'='*60}")
        print(f"❌ ERROR: Grid does not fit on paper!")
        print(f"{'='*60}")
        print(f"Configuration:")
        print(f"  Paper: {paper_width_mm}mm × {paper_height_mm}mm ({orientation})")
        print(f"  Card size: {card_width_mm}mm × {card_height_mm}mm")
        print(f"  Grid: {grid_cols} columns × {grid_rows} rows")
        print(f"  Gap between cards: {gap_mm}mm")
        print(f"\nSpace required:")
        print(f"  Width needed:  {total_width_needed:.1f}mm")
        print(f"  Height needed: {total_height_needed:.1f}mm")
        print(f"\nSpace available:")
        print(f"  Width available:  {paper_width_mm}mm {'✓' if width_fits else '✗ TOO SMALL'}")
        print(f"  Height available: {paper_height_mm}mm {'✓' if height_fits else '✗ TOO SMALL'}")

        # Calculate what would fit
        max_cols = int((paper_width_mm + gap_mm) / (card_width_mm + gap_mm))
        max_rows = int((paper_height_mm + gap_mm) / (card_height_mm + gap_mm))

        print(f"\n💡 Suggestions:")
        print(f"  • Maximum grid that fits: {max_cols} × {max_rows} cards")

        if orientation == "portrait":
            # Suggest landscape if it would help
            landscape_max_cols = int((paper_height_mm + gap_mm) / (card_width_mm + gap_mm))
            landscape_max_rows = int((paper_width_mm + gap_mm) / (card_height_mm + gap_mm))
            if landscape_max_cols >= grid_cols and landscape_max_rows >= grid_rows:
                print(f"  • Try landscape orientation instead")
                print(f"    (would allow {landscape_max_cols} × {landscape_max_rows} cards)")
        else:
            # Suggest portrait if it would help
            portrait_max_cols = int((paper_height_mm + gap_mm) / (card_width_mm + gap_mm))
            portrait_max_rows = int((paper_width_mm + gap_mm) / (card_height_mm + gap_mm))
            if portrait_max_cols >= grid_cols and portrait_max_rows >= grid_rows:
                print(f"  • Try portrait orientation instead")
                print(f"    (would allow {portrait_max_cols} × {portrait_max_rows} cards)")

        print(f"  • Reduce grid size in your config file")
        print(f"  • Use larger paper")
        print(f"  • Use smaller cards")
        print(f"{'='*60}\n")

        sys.exit(1)


def _print_summary(
    image_files,
    paper_width_mm,
    paper_height_mm,
    card_width_mm,
    card_height_mm,
    gap_mm,
    dpi,
    cards_per_page,
    grid_cols,
    grid_rows,
    total_pages,
    orientation,
):
    """Print initial summary of configuration."""
    paper_width_inches = paper_width_mm / 25.4
    paper_height_inches = paper_height_mm / 25.4
    card_width_inches = card_width_mm / 25.4
    card_height_inches = card_height_mm / 25.4

    print(f"{'='*60}")
    print(f"CARD SHEET GENERATOR")
    print(f"{'='*60}")
    print(f"✓ Found {len(image_files)} card images")
    print(
        f"✓ Paper: {paper_width_mm}mm × {paper_height_mm}mm ({paper_width_inches:.1f}\" × {paper_height_inches:.1f}\")"
    )
    print(f"✓ Orientation: {orientation.upper()}")
    print(
        f"✓ Card size: {card_width_mm}mm × {card_height_mm}mm ({card_width_inches:.2f}\" × {card_height_inches:.2f}\")"
    )
    print(f"✓ Gap between cards: {gap_mm}mm")
    print(f"✓ Resolution: {dpi} DPI")
    print(f"✓ Cards per page: {cards_per_page} ({grid_cols} × {grid_rows})")
    print(f"✓ Total pages needed: {total_pages}")


def _save_pages(pages, output_path, output_dir, dpi):
    """Save pages as PDF or PNG files."""
    print(f"\n{'='*60}")
    print(f"SAVING FILES...")
    print(f"{'='*60}")

    if output_path.lower().endswith(".pdf"):
        # Save as multi-page PDF
        if len(pages) == 1:
            pages[0].save(output_path, "PDF", resolution=dpi, quality=100)
            print(f"✓ Created: {output_path} (1 page)")
        else:
            # First page as base, rest as append
            pages[0].save(
                output_path,
                "PDF",
                resolution=dpi,
                quality=100,
                save_all=True,
                append_images=pages[1:],
            )
            print(f"✓ Created: {output_path} ({len(pages)} pages)")
    else:
        # Save as multiple PNG files with suffixes
        base_name = os.path.splitext(output_path)[0]
        ext = os.path.splitext(output_path)[1]

        if len(pages) == 1:
            # Single page - no suffix needed
            pages[0].save(
                output_path, "PNG", dpi=(dpi, dpi), optimize=False, compress_level=0
            )
            print(f"✓ Created: {output_path}")
        else:
            # Multiple pages - add suffixes
            for i, page in enumerate(pages):
                filename = f"{base_name}_{i+1}{ext}"
                page.save(
                    filename, "PNG", dpi=(dpi, dpi), optimize=False, compress_level=0
                )
                print(f"✓ Created: {filename}")


def _print_final_summary(
    config,
    paper_width_mm,
    paper_height_mm,
    grid_cols,
    grid_rows,
    cards_per_page,
    dpi,
    paper_width_px,
    paper_height_px,
    image_files,
    total_pages,
    card_width_mm,
    card_height_mm,
    card_width_px,
    card_height_px,
    gap_mm,
    start_x,
    start_y,
    mm_to_pixels,
    orientation,
):
    """Print final summary with print settings."""
    paper_width_inches = paper_width_mm / 25.4
    paper_height_inches = paper_height_mm / 25.4
    card_width_inches = card_width_mm / 25.4
    card_height_inches = card_height_mm / 25.4

    print(f"\n{'='*60}")
    print(f"✓ SUCCESS!")
    print(f"{'='*60}")
    print(
        f"  Paper: {paper_width_mm}mm × {paper_height_mm}mm ({paper_width_inches:.1f}\" × {paper_height_inches:.1f}\")"
    )
    print(
        f"  Layout: {grid_cols} columns × {grid_rows} rows = {cards_per_page} cards per page"
    )
    print(f"  Resolution: {dpi} DPI")
    print(f"  Image size: {paper_width_px} × {paper_height_px} pixels")
    print(f"  Total cards: {len(image_files)}")
    print(f"  Total pages: {total_pages}")
    print(
        f"  Card size: {card_width_mm}mm × {card_height_mm}mm ({card_width_px} × {card_height_px} pixels)"
    )
    print(f"  Gap between cards: {gap_mm}mm")
    print(
        f"  Cut marks: RGB({config['MARK_COLOR_R']},{config['MARK_COLOR_G']},{config['MARK_COLOR_B']})"
    )
    print(f"\n  Margins:")
    print(f"    Left/Right: {start_x/mm_to_pixels:.1f}mm")
    print(f"    Top/Bottom: {start_y/mm_to_pixels:.1f}mm")
    print(f"\n{'='*60}")
    print(f"📄 CRITICAL PRINT SETTINGS:")
    print(f"{'='*60}")
    print(
        f"  ⚠️  Paper size: {paper_width_mm}mm × {paper_height_mm}mm ({paper_width_inches:.1f}\" × {paper_height_inches:.1f}\")"
    )
    print(f"  ⚠️  Orientation: {orientation.upper()}")
    print(f"  ⚠️  Borderless printing: ENABLED")
    print(f"  ⚠️  Scale: 100% - DO NOT SCALE OR 'FIT TO PAGE'")
    print(f"  ⚠️  Quality: Best/Maximum/High")
    print(f"  ⚠️  Color: Full Color")
    print(f"  ⚠️  Page Scaling: None/Actual Size")
    print(f"\n  In printer dialog:")
    print(f"    • Paper: Check config for exact size")
    print(f"    • Orientation: {orientation.upper()}")
    print(f"    • Borderless: ON")
    print(f"    • UNCHECK 'Fit to page'")
    print(f"    • UNCHECK 'Shrink to fit'")
    print(f"    • CHECK 'Actual size' or '100%'")
    print(f"    • Set custom scale to: 100%")
    print(
        f"\n✂️  Cut along corner marks for exact {card_width_mm}mm × {card_height_mm}mm cards!"
    )
    print(f"\n📏 After printing, verify with ruler:")
    print(
        f"   Card width should be: {card_width_mm}mm ({card_width_inches:.2f} inches)"
    )
    print(
        f"   Card height should be: {card_height_mm}mm ({card_height_inches:.2f} inches)"
    )
