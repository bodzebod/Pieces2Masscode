from pieces_os_client.wrapper import PiecesClient

pieces_client = PiecesClient()

# Get all assets and print their names
assets = pieces_client.assets()
for asset in assets:
   print(f"Asset Name: {asset.name} -> classification: {asset.classification.value}")

# Close the client
pieces_client.close()