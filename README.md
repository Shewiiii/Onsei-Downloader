# Onsei Downloader
A simple script to download Audio works (音声作品) from a certain website.

## Requirements
- Python 3.8 or above. You can download it from [python.org](https://www.python.org/).
- `requests` and `music_tag` packages:
```bash
pip install -r requirements.txt
```

## Configuration
Before running the script, rename the `config.json.template` file to `config.json` and complete it with the desired values:
```json
{
  "rootPath": "/path/to/download/folder",
  "ignore": ["wav", "SEなし", "other_extensions_or_folder_to_ignore"]
}

```
- `rootPath`: The base directory where files will be downloaded.
- `ignore`: List of file extensions or folder names to ignore during the download process.

## Usage
1. **Run the script**:
```bash
python3 main.py
```
2. **Input the RJ/VJ code(s)**:   
When prompted, enter the RJ/VJ code(s) separated by commas. Example:
```
RJ401708,RJ240668
```
3. **Done !**
