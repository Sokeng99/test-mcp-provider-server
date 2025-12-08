"""
Package Teams app into a ZIP file
"""
import zipfile
import os

# Files to include in the package
files = ['manifest.json', 'color.png', 'outline.png']

# Create ZIP file
zip_path = '../xpilot-bot-teams-app.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in files:
        if os.path.exists(file):
            zipf.write(file, file)
            print(f"Added {file}")
        else:
            print(f"Warning: {file} not found!")

print(f"\nTeams app package created: {os.path.abspath(zip_path)}")
print("This file is ready to upload to Microsoft Teams!")
