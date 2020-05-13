# exif-timestamp-fix
Simple python script to fix the create/modify date of photo files.
When you export some photos from the Apple Photos App, for example, every exported file contains the datetime of the export. This can cause problems if you want to later import these photos back in the Photos Apps or in any photo library.
This script searches for common timestamp tags to replace the wrong create/modify date.
## Usage
`python3 FixTimestamp.py /path/to/photos/folder/`
