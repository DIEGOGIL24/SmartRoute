# SmartRoute

# Autores
**Julian David Bocanegra Segura** Cod: 202220214<br> 
**Diego Alejandro Gil Otálora** Cod:202222152<br> 
Universidad Pedagógica y Tecnológica de Colombia  
Ingeniería de Sistemas y Computación - Sistemas Distribuidos  
Tunja, 2025 


## Descripción

SmartRoute es un sistema distribuido basado en microservicios y agentes inteligentes, diseñado para generar itinerarios de viaje personalizados según el contexto del usuario y las condiciones climáticas del destino.

El sistema combina procesamiento de lenguaje natural (LangChain y CrewAI) con servicios externos de clima, y se comunica de forma asíncrona mediante RabbitMQ.
La información se almacena y gestiona en una base de datos PostgreSQL, desplegada junto con los demás servicios en contenedores Docker, orquestados mediante docker-compose y balanceados con Traefik.

A diferencia de un generador tradicional que entrega un texto fijo, SmartRoute permite que los itinerarios se actualicen dinámicamente cuando cambian las condiciones del entorno (por ejemplo, si el clima se altera).

## Ejecucion

Levantamos el contenedor de Ollama: <br>

`docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama`

Para ejecutar el proyecto se tiene que ejecutar primero el backend, nos ubicamos en la carpeta raiz del proyecto y ejecutamos <br>
`docker compose up -d`

Posteriormente en otra terminal ejecutamos el frontend, para esto nos ubicamos en la carpeta frontend y ejecutamos <br>

`npm install modules` <br>
`npm run dev`

con esto ya se conectan los 2



