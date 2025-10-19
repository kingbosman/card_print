# Card Print Generator

A modular Python tool for generating printable sheets of cards with precise cut marks. Perfect for creating proxies, game cards, or any custom card printing needs. This tool was created to remain card quality since the tools I found were poor quality.

## Features

- **Unlimited cards**: Automatically splits cards into multiple pages
- **Multiple output formats**: PNG (multiple files) or PDF (single multi-page file)
- **Precise cut marks**: Configurable corner marks at each card corner
- **Flexible configuration**: All settings in easy-to-edit config file
- **High quality**: 300 DPI output with LANCZOS resampling

## Project Structure

```
card_print/
├── config/
│   └── current.config          # Configuration file
├── src/
│   ├── __init__.py             # Package initialization
│   ├── config_loader.py        # Configuration loading
│   ├── page_builder.py         # Page creation logic
│   └── sheet_generator.py      # Main generation logic
├── cards/                       # Your card images go here
├── generate.py                  # Main entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

1. **Add your card images** to the `cards/` folder
   - Supported formats: PNG, JPG, JPEG, WEBP, BMP

2. **Configure settings** in `config/current.config`
   - On first run, if `current.config` doesn't exist, it will be automatically created from `default.config`
   - Set paper size, card dimensions, grid layout, etc.

3. **Run the generator**:
   ```bash
   source venv/bin/activate #only if not already in venv
   python generate.py
   ```
   Note: You can pass in an argument to a specific config if you don't want to overwrite the current.config
   ```bash
   python generate.py config/bears_card_game.config
   ```


4. **Find your output** in the `outputs/` folder
   - Files are timestamped: `outputs/1729534821_sheet.pdf`
   - Each run creates unique files (no overwriting)
   - PNG and PDF allowed for png multiple files are created with suffix _1 , _2 etc

### Configuration

The tool uses a two-tier configuration system:

- **`config/default.config`**: Template with default settings (don't modify)
- **`config/current.config`**: Your active configuration

**First Run**: If `current.config` doesn't exist, it's automatically created from `default.config`.

- To save current config to a config fot later user use `mv config/current.config config/bears_card_game.config && cp config/default.config config/current.config` replace 'bears_card_game' with a desired name

Edit `config/current.config` to customize your output

### Output Formats

**PDF**:
```ini
OUTPUT_FILE = output.pdf
```
- Creates a single multi-page PDF
- Easy to print all pages at once

**PNG**:
```ini
OUTPUT_FILE = output.png
```
- Creates multiple files: `output_1.png`, `output_2.png`, etc.
- One file per page (8 cards each)

## Printing

### Critical Print Settings

⚠️ **Important**: Use these settings to ensure correct card sizes:

1. **Paper size**: Match your config (default: Letter 279.4mm × 215.9mm)
2. **Orientation**: Match your config (default Landscape)
3. **Borderless printing**: ENABLED
4. **Scale**: 100% - DO NOT SCALE OR 'FIT TO PAGE'
5. **Quality**: Best/Maximum/High
6. **Color**: Full Color

### Printer Dialog Checklist

- [ ] Paper: LETTER (or size from config)
- [ ] Orientation: LANDSCAPE (or Portrait if set in config)
- [ ] Borderless: ON
- [ ] UNCHECK 'Fit to page'
- [ ] UNCHECK 'Shrink to fit'
- [ ] CHECK 'Actual size' or '100%'
- [ ] Set custom scale to: 100%

### After Printing

Verify dimensions with a ruler:
- Card width should be: 63mm (2.48 inches) - or your configured size
- Card height should be: 88mm (3.46 inches) - or your configured size

Cut along the corner marks for precise cards!

## Module Documentation

### `src/config_loader.py`
Handles loading and parsing configuration files.

### `src/page_builder.py`
Creates individual pages with cards and cut marks. Contains:
- `create_single_page()`: Main page creation function
- `_place_cards()`: Places card images in grid
- `_add_corner_marks()`: Adds cut marks at corners
- `_add_guide_lines()`: Adds grid guide lines

### `src/sheet_generator.py`
Main sheet generation logic. Contains:
- `generate_sheets()`: Main entry point
- Helper functions for file handling and output

## Troubleshooting

**Cards are the wrong size after printing**:
- Verify printer settings (100% scale, no fit-to-page)
- Check that borderless printing is enabled
- Ensure correct paper size is selected

**Corner marks not visible**:
- Increase `GAP_MM` in config (try 2-3mm)
- Change mark color if printing on colored paper
- Increase `MARK_LENGTH_MM` and `MARK_WIDTH_PX`

**No images found**:
- Check that images are in the folder specified by `CARD_IMAGES_FOLDER`
- Verify image format is supported (PNG, JPG, JPEG, WEBP, BMP)

**Config file not found error**:
- Ensure `config/default.config` exists in the project
- If missing, restore from repository or recreate it
- On first run, `current.config` will be created automatically from `default.config`

## Extra notes
- The tool is tested in a Linux environment.
- Windows users might need to use WSL to follow along the provided steps. Don't forget to `sudo apt update && sudo apt upgrade -y`

## License

This project is open source and available for personal use.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool!
