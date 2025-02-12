import json
import sys
import traceback
from pathlib import Path
from datetime import datetime

# Force stdout to flush immediately
import functools
print = functools.partial(print, flush=True)

print("Starting program...")
sys.stdout.flush()

try:
    print("Importing PiecesToMassCodeConverter...")
    sys.stdout.flush()
    from converter import PiecesToMassCodeConverter
    print("Successfully imported PiecesToMassCodeConverter")
    sys.stdout.flush()
except Exception as e:
    print(f"Error importing converter: {e}", file=sys.stderr)
    print("Traceback:", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

def main():
    print("\n=== Starting Pieces to massCode conversion ===")
    
    try:
        print("\nInitializing converter...")
        converter = PiecesToMassCodeConverter()
        
        print("\nConverting assets...")
        db = converter.convert()
        
        print("\nConversion statistics:")
        print(f"- Created folders: {len(db.folders)}")
        print(f"- Created tags: {len(db.tags)}")
        print(f"- Processed snippets: {len(db.snippets)}")
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"masscode_export_{timestamp}.json")
        
        # Save the converted database
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(db.dict(), f, indent=2)
        
        print(f"\n=== Conversion completed successfully! ===")
        print(f"- Total snippets exported: {len(db.snippets)}")
        print(f"- Total tags created: {len(db.tags)}")
        print(f"- Output file: {output_file.absolute()}")
        
    except Exception as e:
        print(f"\nError during conversion: {str(e)}", file=sys.stderr)
        print("\nPlease ensure that:", file=sys.stderr)
        print("1. Pieces OS is running", file=sys.stderr)
        print("2. You have snippets saved in Pieces", file=sys.stderr)
        print("3. The virtual environment is activated", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
