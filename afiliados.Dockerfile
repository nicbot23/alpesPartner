FROM python:3.12

EXPOSE 8300/tcp

COPY afiliados-requirements.txt ./
RUN pip install --upgrade --no-cache-dir pip setuptools wheel
RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir -r afiliados-requirements.txt

COPY . .

WORKDIR "/src-alpespartner"

CMD [ "uvicorn", "afiliados.main:app", "--host", "0.0.0.0", "--port", "8300", "--reload"]