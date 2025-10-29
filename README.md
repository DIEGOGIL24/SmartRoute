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
Para ejecutar el proyecto se tiene que ejecutar primero el backend, nos ubicamos en la carpeta raiz del proyecto y ejecutamos <br>
`docker compose up -d` <br> 

Posteriormente tendremos que descargar el modelo `qwen3` dentro de ollama, para esto entramos al contenedor <br> 
`docker exec -it ollamaSmartRoute bash`<br> 
Luego instalamos qwen3 <br> 
`ollama pull qwen3`<br> 

Con esto ya podemos ejecutar los endpoints 

Para ver el consumo en tiempo real de la GPU podemos ejecutar `watch -n 1 nvidia-smi` dentro de Ollama






