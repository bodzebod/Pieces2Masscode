# Pieces to massCode Converter

A Python tool to export code snippets from Pieces for Developers to massCode format.

## Prerequisites

- Python 3
- Pieces OS installed and running locally
- Virtual environment "pieces_for_developers" (created with uv)

## Setup

1. Activate the virtual environment:
```powershell
.\.venv\Scripts\activate.ps1
```

2. Ensure Pieces OS is running locally

## Usage

Simply run the main script:
```powershell
python src/main.py
```

The program will:
1. Connect to your local Pieces OS instance
2. Fetch all your saved snippets
3. Convert them to massCode format
4. Save them in a JSON file named `masscode_export_[timestamp].json`

## Features

- Automatic language detection and folder organization
- Tag preservation
- Snippet metadata preservation
- Timeout handling (3 minutes max for fetching assets)
- Cross-platform support
- Detailed progress logging

## Output

The program creates a JSON file that can be imported directly into massCode. Snippets are organized by:
- Language-specific folders
- Original tags
- Original metadata (name, description, etc.)

## Error Handling

The program will display helpful error messages if:
- Pieces OS is not running
- No snippets are found
- The virtual environment is not activated
- Any other issues occur during conversion

## Project Structure

- `src/main.py` - Main entry point
- `src/converter.py` - Core conversion logic
- `src/models/masscode.py` - massCode data models
- `samples/` - Sample files and SDK reference
