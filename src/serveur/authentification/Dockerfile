FROM python:latest

# Set noninteractive mode for apt-get
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y --no-install-recommends   \
       python3-pip pipx curl


RUN adduser --disabled-password --gecos "" toto
USER toto
WORKDIR /home/toto
ADD oauth.tgz /home/toto
RUN ls 
RUN pipx install uv
RUN /home/toto/.local/bin/uv sync

CMD ["/home/toto/.local/bin/uv", "run", "/home/toto/app.py"]
