#!/bin/bash
set -e

mkdir -p services

if [ ! -d services/chokak-server ]; then
    git clone https://github.com/Rostelecom-Practice/chokak-server.git services/chokak-server
fi

if [ ! -d services/chokak-gateway-server ]; then
    git clone https://github.com/Rostelecom-Practice/chokak-gateway-server.git services/chokak-gateway-server
fi

if [ ! -d services/chokak-cloud-storage ]; then
    git clone https://github.com/Rostelecom-Practice/chokak-cloud-storage.git services/chokak-cloud-storage
fi

if [ ! -d services/external-service-example ]; then
    git clone https://github.com/Rostelecom-Practice/external-service-example.git services/external-service-example
fi

