# Onsei Downloader
A simple script to download Audio works (音声作品) from a certain website.

## Requirements
- Python 3.8 or above. You can download it from [python.org](https://www.python.org/).
- `requests` and `music_tag` packages:
```bash
pip3 install -r requirements.txt
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
### Running the Script from the Command Line
**Fastest way**, directly parse RJ/VJ code(s) as a command-line argument:
```bash
python3 main.py RJ401708,RJ240668
```
OR
1. **Run the script**:
```bash
python3 main.py
```
2. **Input the RJ/VJ code(s)**:   
When prompted, enter the RJ/VJ code(s) separated by commas.
```
RJ401708,RJ240668
```
3. **Done !**
### Using the Script in Python
1. **Import the script**:
```python
from main import download_onsei
```
2. **Call the** `download_onsei` **function**:   
Pass the RJ/VJ code as a string to the function.
```python
code = "RJ401708"
download_onsei(code)
```
3. **That's all !**

