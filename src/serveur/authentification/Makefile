all: tar
	docker  build -t authentification .
	#sudo docker  build --progress=plain -t authentification .

run:
	docker run -ti -p 5000:5000 --name authentification authentification

debug:
	docker logs authentification

clean:
	rm -f oauth.tgz
	docker rm authentification

tar:
	tar czvf oauth.tgz app.py Dockerfile Makefile pyproject.toml README templates/
