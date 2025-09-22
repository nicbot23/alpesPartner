FROM python:3.12

EXPOSE 8000/tcp

COPY campanias-requirements.txt ./
RUN pip install --upgrade --no-cache-dir pip setuptools wheel
RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir -r campanias-requirements.txt

COPY . .

WORKDIR "/src-alpespartner"

CMD [ "uvicorn", "campanias.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]