# PackingUtils

## install the package
```
# (optional) 
python -m venv env
env\Scripts\activate # Windows

git clone https://github.com/ArnoSchiller/PackingUtils.git
git pull
pip install -e PackingUtils
```
### Unit tests
```
cd PackungUtils
python -m unittest 
```
## Requirements
**greedypacker does not work with Python 3.10**, use 3.8 instead: 
```bash 
C:\Python\Python38\python.exe -m venv env
```

Install the packages needed for this project
```bash
pip install -r requirements.txt
```

## Example usage
```bash
python packing_utils/heuristic_2D.py
```