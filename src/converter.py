import uuid
import sys
import threading
import traceback
import platform
from datetime import datetime
from typing import Dict, List, Optional

# Force stdout to flush immediately
import functools
print = functools.partial(print, flush=True)

import pieces_os_client
from pieces_os_client.wrapper import PiecesClient
from pieces_os_client.models.classification_specific_enum import ClassificationSpecificEnum

from models.masscode import MassCodeDB, Snippet, SnippetContent, Tag, Folder

class TimeoutError(Exception):
    """Raised when an operation times out"""
    pass

def generate_id() -> str:
    """Generate a unique ID for massCode entities"""
    return str(uuid.uuid4())[:8]

def get_language_from_classification(classification: Optional[str]) -> str:
    """Convert Pieces classification to massCode language"""
    if not classification:
        return "plain_text"
    
    # Map Pieces classifications to massCode languages
    language_map = {
        'py': 'python',
        'py3': 'python',
        'pyw': 'python',
        'js': 'javascript',
        'jsx': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescript',
        'html': 'html',
        'htm': 'html',
        'css': 'css',
        'scss': 'css',
        'json': 'json',
        'md': 'markdown',
        'markdown': 'markdown',
        'sh': 'shell',
        'bash': 'shell',
        'zsh': 'shell',
        'sql': 'sql',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'cs': 'csharp',
        'php': 'php',
        'php3': 'php',
        'php4': 'php',
        'php5': 'php',
        'php7': 'php',
        'php8': 'php',
        'rb': 'ruby',
        'ruby': 'ruby',
        'rs': 'rust',
        'go': 'go',
        'xml': 'xml',
        'yaml': 'yaml',
        'yml': 'yaml',
        'ini': 'ini',
        'dockerfile': 'dockerfile',
        'ps1': 'powershell',
        'swift': 'swift',
        'kt': 'kotlin',
        'scala': 'scala',
        'r': 'r',
        'tex': 'tex',
        'lua': 'lua',
        'perl': 'perl',
        'pl': 'perl',
        'dart': 'dart',
        'elm': 'elm',
        'erl': 'erlang',
        'fs': 'fsharp',
        'groovy': 'groovy',
        'hs': 'haskell',
        'matlab': 'matlab',
        'm': 'matlab',
        'mm': 'objective-c',
        'vue': 'vue',
        'svelte': 'svelte',
        'tf': 'terraform',
        'sol': 'solidity'
    }
    return language_map.get(str(classification.value).lower(), "plain_text")

class PiecesToMassCodeConverter:
    def __init__(self):
        print("Initializing PiecesToMassCodeConverter...")
        print("Creating MassCode database structure...")
        self.db = MassCodeDB(folders=[], snippets=[], tags=[])
        self.tag_map: Dict[str, str] = {}  # Maps Pieces tag names to massCode tag IDs
        self.folder_map: Dict[str, str] = {}  # Maps languages to folder IDs
        self.pieces_client = None
        
        # Initialize language folders
        print("Creating language folders...")
        self._create_language_folders()
        print(f"Created {len(self.db.folders)} language folders")

    def _ensure_pieces_client(self):
        """Ensure Pieces OS client is initialized"""
        if self.pieces_client is None:
            print("Checking if Pieces OS is running...")
            try:
                # Determine the correct port based on OS
                port = 5323 if 'Linux' in platform.platform() else 1000
                
                # Create the wrapper client
                self.pieces_client = PiecesClient(host=f"http://localhost:{port}")
                
                # Test connection by getting assets
                test_assets = self.pieces_client.assets()
                print("Successfully connected to Pieces OS")
            except Exception as e:
                print(f"Error connecting to Pieces OS: {e}")
                print("Please ensure Pieces OS is running and try again")
                self.pieces_client = None
                raise
    
    def _create_language_folders(self):
        """Create folders for each supported language"""
        now = int(datetime.now().timestamp() * 1000)
        
        # Create root folder for uncategorized snippets
        default_id = generate_id()
        default_folder = Folder(
            id=default_id,
            name="Default",
            defaultLanguage="plain_text",
            createdAt=now,
            updatedAt=now
        )
        self.db.folders.append(default_folder)
        self.folder_map["plain_text"] = default_id
        
        # Define language folders
        languages = {
            "python": "Python",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "html": "HTML",
            "css": "CSS",
            "json": "JSON",
            "markdown": "Markdown",
            "shell": "Shell",
            "sql": "SQL",
            "java": "Java",
            "cpp": "C++",
            "c": "C",
            "csharp": "C#",
            "php": "PHP",
            "ruby": "Ruby",
            "rust": "Rust",
            "go": "Go",
            "xml": "XML",
            "yaml": "YAML",
            "ini": "INI",
            "dockerfile": "Dockerfile",
            "powershell": "PowerShell",
            "swift": "Swift",
            "kotlin": "Kotlin",
            "scala": "Scala",
            "r": "R",
            "tex": "TeX",
            "lua": "Lua",
            "perl": "Perl",
            "dart": "Dart",
            "elm": "Elm",
            "erlang": "Erlang",
            "fsharp": "F#",
            "groovy": "Groovy",
            "haskell": "Haskell",
            "matlab": "MATLAB",
            "objective-c": "Objective-C",
            "vue": "Vue",
            "svelte": "Svelte",
            "terraform": "Terraform",
            "solidity": "Solidity"
        }
        
        # Create a folder for each language
        for lang_key, lang_name in languages.items():
            folder_id = generate_id()
            folder = Folder(
                id=folder_id,
                name=lang_name,
                defaultLanguage=lang_key,
                createdAt=now,
                updatedAt=now
            )
            self.db.folders.append(folder)
            self.folder_map[lang_key] = folder_id

    def _create_or_get_tag(self, tag_name: str) -> str:
        """Create a new tag or get existing tag ID"""
        print(f"\nCreating/getting tag: {tag_name}")
        if tag_name in self.tag_map:
            print(f"Found existing tag ID: {self.tag_map[tag_name]}")
            return self.tag_map[tag_name]
        
        now = int(datetime.now().timestamp() * 1000)
        tag_id = generate_id()
        new_tag = Tag(
            id=tag_id,
            name=tag_name,
            createdAt=now,
            updatedAt=now
        )
        print(f"Created new tag: {new_tag}")
        self.db.tags.append(new_tag)
        self.tag_map[tag_name] = tag_id
        print(f"Total tags in database: {len(self.db.tags)}")
        return tag_id

    def _get_folder_id(self, language: str) -> str:
        """Get folder ID for a given language, fallback to default if not found"""
        return self.folder_map.get(language, self.folder_map["plain_text"])

    def _convert_asset_to_snippet(self, asset) -> Snippet:
        """Convert a Pieces asset to a massCode snippet"""
        now = int(datetime.now().timestamp() * 1000)
        
        # For debugging
        print(f"Asset structure: {dir(asset)}")
        print(f"Asset tags: {asset.tags if hasattr(asset, 'tags') else 'No tags attribute'}")
        if hasattr(asset, 'tags'):
            print(f"Tags type: {type(asset.tags)}")
            print(f"Tags content: {asset.tags}")
        
        try:
            # Try to get the raw content and metadata
            content_value = asset.raw_content if hasattr(asset, 'raw_content') else str(asset)
            name = asset.name if hasattr(asset, 'name') and asset.name else "Untitled snippet"
            description = asset.description if hasattr(asset, 'description') else None
            
            # Get language from asset classification
            language = "plain_text"
            if hasattr(asset, 'classification'):
                print(f"Found classification: {asset.classification}")
                language = get_language_from_classification(asset.classification)
            print(f"Using language: {language}")
            
            # Create snippet content
            snippet_content = [
                SnippetContent(
                    label="Fragment 1",
                    language=language,
                    value=content_value
                )
            ]
            
            # Handle tags - safely
            tag_ids = []
            if hasattr(asset, 'tags') and asset.tags:
                print(f"Processing tags: {asset.tags}")
                for tag in asset.tags:
                    print(f"Processing tag: ID: {tag.id}")
                    try:
                        # Get the tag text value from the Pieces OS Tag model's text property
                        tag_name = tag.tag.text
                        if not tag_name:
                            print(f"Warning: Tag {tag.id} has empty tag.text property")
                            continue
                        
                        print(f"Adding tag: {tag_name}")
                        tag_ids.append(self._create_or_get_tag(tag_name))
                    except AttributeError as e:
                        print(f"Error accessing tag.text for tag {tag.id}: {e}")
                        print("This suggests the tag object doesn't match the expected Pieces OS SDK Tag model structure")
                        continue
                    except Exception as e:
                        print(f"Unexpected error processing tag {tag.id}: {e}")
                        continue
            
            # Get appropriate folder ID based on language
            folder_id = self._get_folder_id(language)
            print(f"Using folder ID: {folder_id} for language: {language}")
            
            # Create and return snippet
            return Snippet(
                id=generate_id(),
                name=name,
                content=snippet_content,
                description=description,
                folderId=folder_id,
                tagsIds=tag_ids,
                createdAt=now,
                updatedAt=now
            )
            
        except Exception as e:
            print(f"Error converting asset: {e}", file=sys.stderr)
            print("Traceback:", file=sys.stderr)
            traceback.print_exc()
            # Return a basic snippet with error information
            return Snippet(
                id=generate_id(),
                name="Error converting snippet",
                content=[SnippetContent(
                    label="Error",
                    language="plain_text",
                    value=f"Error converting snippet: {str(e)}\nOriginal asset: {str(asset)}"
                )],
                description="Error occurred during conversion",
                folderId=self.db.add_default_folder(),
                tagsIds=[],
                createdAt=now,
                updatedAt=now
            )

    def convert(self) -> MassCodeDB:
        """Convert all Pieces assets to massCode format"""
        try:
            # Ensure Pieces OS client is initialized
            self._ensure_pieces_client()
            
            print("\nSetting up 5-minute timeout for fetching assets...")
            timeout_event = threading.Event()
            assets = None
            asset_count = 0
            error = None

            def fetch_assets():
                nonlocal assets, error
                try:
                    assets = self.pieces_client.assets()
                except Exception as e:
                    error = e

            # Start asset fetching in a separate thread
            thread = threading.Thread(target=fetch_assets)
            thread.start()
            
            # Wait for thread to complete or timeout with periodic status updates
            total_wait = 300  # 5 minutes = 300 seconds
            interval = 30  # Check every 30 seconds
            waited = 0
            
            while thread.is_alive() and waited < total_wait:
                print(f"Waiting for assets... ({waited} seconds elapsed)")
                if thread.join(timeout=interval):
                    break
                waited += interval
            
            if thread.is_alive():
                error = TimeoutError("Operation timed out after 5 minutes - Pieces OS is taking too long to respond")
                # Force close the client to stop any ongoing operations
                try:
                    self.pieces_client.close()
                except:
                    pass
                self.pieces_client = None
                raise error

            if error:
                if isinstance(error, TimeoutError):
                    print(f"\nError: {error}")
                    print("Please try again or check if Pieces OS is running properly")
                else:
                    print(f"Error fetching assets: {error}")
                raise error

            asset_count = len(assets) if assets else 0
            print(f"Successfully retrieved {asset_count} assets from Pieces")
            
            # Convert each asset to a snippet
            for i, asset in enumerate(assets, 1):
                print(f"\nProcessing asset {i}/{len(assets)}")
                snippet = self._convert_asset_to_snippet(asset)
                self.db.snippets.append(snippet)
            
            print("\nFinal database statistics:")
            print(f"- Total snippets: {len(self.db.snippets)}")
            print(f"- Total tags: {len(self.db.tags)}")
            print(f"- Tag names: {[tag.name for tag in self.db.tags]}")
            
            return self.db
        finally:
            if self.pieces_client is not None:
                try:
                    self.pieces_client.close()
                except:
                    pass
