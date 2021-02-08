FROM joyzoursky/python-chromedriver:3.7


RUN pip install poetry

COPY . /usr/workspace 

WORKDIR /usr/workspace

RUN poetry install


ENV BFETCH="/usr/workspace"
ENV PATH="/usr/workspace/:${PATH}"


CMD ["poetry", "run", "python", "/usr/workspace/bfetch/main.py"]
