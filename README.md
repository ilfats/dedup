dedup
=====

Deduplicator for Coursera offline files downloaded with coursera-dl


usage
=====

deduplicate.py [-h] [--remove] path_name

Find/remove duplicates in downloaded Coursera content

positional arguments:
  path_name   Path to process (e.g., C:\Coursera)

optional arguments:
  -h, --help  show this help message and exit
  --remove    remove detected duplicates keeping only the latest version. Use
              at your own risk!
