FROM gaivoronsky/base-docker:latest

COPY pyproject.toml ./pyproject.toml
RUN poetry run pip3 install -U pip
RUN poetry self update
RUN poetry lock
RUN poetry install --no-interaction --no-dev

# PJSIP
RUN apt install python python-dev build-essential libasound2-dev libportaudio2 -y
RUN wget https://github.com/DiscordPhone/pjproject/archive/py37.zip
RUN unzip py37.zip
RUN chmod +x pjproject-py37/configure pjproject-py37/aconfigure

WORKDIR pjproject-py37/
RUN ./configure CXXFLAGS=-fPIC CFLAGS=-fPIC LDFLAGS=-fPIC CPPFLAGS=-fPIC
RUN make dep
RUN make
RUN make install

# PJSUA
WORKDIR pjsip-apps/src/python/
RUN python setup.py build
RUN python setup.py install

# softphone
WORKDIR /
RUN python -m pip install https://github.com/ArtIntlabs/softphone/archive/master.zip --user

EXPOSE 80
COPY .env.tmpl ./.env.tmpl
COPY example.py ./example.py
CMD python example.py