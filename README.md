<div align="center">    

# PackingUtils
</div>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Install the package
```
# (optional) 
python -m venv env
env\Scripts\activate # Windows

git clone https://github.com/ArnoSchiller/PackingUtils.git
git pull
cd PackingUtils
pip install -e .
pip install -r requirements.txt
```
### Unit test the project
*info*: Make sure you are inside of the project directory.
```
python -m unittest 
```

### Add additional dependencies
**important:** greedypacker does only work with python 3.8:
```
C:\Python\Python38\python.exe -m venv env
```

The following dependencies are optional. Select the module you want to use and install the required package. 

*info*: The unittests of this project also check dependencies and give information to install them.

```bash
# Module: GreedyPacker
pip install -r requirements_greedy.txt 

# Module: Py3dbpPacker
pip install py3dbp
```


## Run the solver API (Docker)
### Build docker image and publish

```bash
cd _api_packing
docker build -t packingsolver .

# (optional)
docker tag packingsolver harbor.swms-cloud.com/binpacking/packingsolver:latest
docker push harbor.swms-cloud.com/binpacking/packingsolver:latest
```

### Run the docker container 
```bash
docker run -p 8000:8000 packingsolver
```
