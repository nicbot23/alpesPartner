FROM python:3.12

EXPOSE 8100/tcp

COPY bff-requirements.txt ./
RUN pip install --upgrade --no-cache-dir pip setuptools wheel
RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir -r bff-requirements.txt

COPY . .

WORKDIR "/src-alpespartner"

CMD [ "uvicorn", "bff.main:app", "--host", "0.0.0.0", "--port", "8100", "--reload"]