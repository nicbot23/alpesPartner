FROM apachepulsar/pulsar:latest

# Copiar script de inicialización
COPY init-pulsar-metadata.sh /init-pulsar-metadata.sh
USER root
RUN chmod +x /init-pulsar-metadata.sh
USER pulsar