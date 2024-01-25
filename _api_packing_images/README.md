### Run the API locally
```
cd api_packing_images
uvicorn api:app --reload
```

### Run the API using docker
- Build docker image and publish
```
cd api_packing_images
docker build -t packingimages .

# (optional)
docker tag packingimages harbor.swms-cloud.com/binpacking/packingimages:1.0
docker push harbor.swms-cloud.com/binpacking/packingimages:1.0
```

- Run the docker container 
```
docker run -p 8000:8000 packingimages
```