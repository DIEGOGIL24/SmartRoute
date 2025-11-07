# SmartRoute 

## Autores
**Julian David Bocanegra Segura** - Cod: 202220214<br> 
**Diego Alejandro Gil Otálora** - Cod: 202222152<br> 
Universidad Pedagógica y Tecnológica de Colombia  
Ingeniería de Sistemas y Computación - Sistemas Distribuidos  
Tunja, 2025

---

## Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Requisitos Previos](#-requisitos-previos)
- [Configuración del Proyecto](#-configuración-del-proyecto)
- [Instalación y Ejecución](#-instalación-y-ejecución)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [APIs y Endpoints](#-apis-y-endpoints)
- [Base de Datos](#-base-de-datos)
- [Troubleshooting](#-troubleshooting)
- [Contribución](#-contribución)

---

## Descripción

**SmartRoute** es un sistema distribuido basado en microservicios y agentes inteligentes, diseñado para generar itinerarios de viaje personalizados según el contexto del usuario y las condiciones climáticas del destino.

### Características Principales

- **Generación Inteligente de Itinerarios**: Utiliza agentes de IA (LangChain y CrewAI) para crear rutas personalizadas
- **Integración con APIs Climáticas**: Consulta en tiempo real las condiciones meteorológicas del destino
- **Recomendaciones Turísticas**: Integración con Google Places API para sugerir lugares de interés
- **Actualización Dinámica**: Los itinerarios se adaptan cuando cambian las condiciones del entorno
- **Comunicación Asíncrona**: Utiliza RabbitMQ para mensajería entre microservicios
- **Persistencia de Datos**: PostgreSQL para almacenar usuarios, itinerarios y datos climáticos
- **Balanceo de Carga**: Traefik como reverse proxy y load balancer
- **Modelos LLM Locales**: Ollama con soporte GPU para procesamiento de lenguaje natural

---

## Arquitectura del Sistema

<img width="2300" height="1671" alt="Diagrama en blanco" src="https://github.com/user-attachments/assets/069cd149-1a01-4f75-98fb-802f9a2c9315" />


### Componentes

1. **Frontend**: Aplicación React + TypeScript con Vite y Shadcn/ui
2. **Backend**: API REST con FastAPI + Python
3. **Agentes Inteligentes**:
   - `weather_agent`: Consulta y procesa datos climáticos
   - `tourism_agent`: Genera recomendaciones turísticas
4. **Ollama**: Servidor de modelos LLM para procesamiento de lenguaje natural
5. **RabbitMQ**: Message broker para comunicación asíncrona entre servicios
6. **PostgreSQL**: Base de datos relacional para persistencia
7. **Traefik**: Reverse proxy y balanceador de carga

---

## Tecnologías Utilizadas

### Backend
- **Python 3.11+**
- **FastAPI** 0.120.1 - Framework web moderno y rápido
- **LangChain** 1.0.3 - Framework para desarrollo con LLMs
- **CrewAI** 1.2.0 - Framework para agentes autónomos de IA
- **Ollama** 0.6.0 - Cliente para modelos LLM locales
- **Pika** 1.3.2 - Cliente RabbitMQ
- **Psycopg2** 2.9.11 - Adaptador PostgreSQL
- **OpenAI** - Integración con modelos de OpenAI/Azure

### Frontend
- **React** 18+
- **TypeScript** 5+
- **Vite** - Build tool
- **Shadcn/ui** - Componentes UI basados en Radix UI
- **TailwindCSS** - Framework CSS
- **React Query** - Gestión de estado del servidor
- **React Hook Form** - Gestión de formularios

### Infraestructura
- **Docker** & **Docker Compose** - Contenedores y orquestación
- **PostgreSQL** 15 - Base de datos
- **RabbitMQ** 3 - Message broker
- **Traefik** 2.10 - Reverse proxy
- **Ollama** - Servidor de modelos LLM

### APIs Externas
- **OpenWeatherMap API** - Datos climáticos
- **Google Places API** - Información de lugares
- **Azure OpenAI** (opcional) - Modelos GPT en la nube

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

### Software Requerido

1. **Docker Desktop** (versión 20.10 o superior)
   - Descarga: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
   - Asegúrate de que Docker Compose esté incluido

2. **Git** (para clonar el repositorio)
   - Descarga: [https://git-scm.com/downloads](https://git-scm.com/downloads)

3. **GPU NVIDIA con CUDA** (opcional, para usar Ollama con aceleración GPU)
   - Drivers NVIDIA actualizados
   - NVIDIA Container Toolkit para Docker
   - Guía: [https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

### Claves API Requeridas

Necesitarás obtener las siguientes claves API:

1. **OpenWeatherMap API Key**
   - Regístrate en: [https://openweathermap.org/api](https://openweathermap.org/api)
   - Plan gratuito disponible (hasta 1000 llamadas/día)

2. **Google Places API Key**
   - Guía: [https://developers.google.com/maps/documentation/places/web-service/get-api-key?hl=es-419](https://developers.google.com/maps/documentation/places/web-service/get-api-key?hl=es-419)
   - Asegúrate de habilitar la API de Places (New)

3. **Azure OpenAI** (opcional, si no usas Ollama)
   - Portal de Azure: [https://portal.azure.com/](https://portal.azure.com/)
   - Crea un recurso de Azure OpenAI Service

---

## Configuración del Proyecto

### Paso 1: Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd SmartRoute
```

### Paso 2: Crear Archivo de Variables de Entorno

Crea un archivo `.env` en la carpeta `backend/` con el siguiente contenido:

```bash
# Navegar a la carpeta backend
cd backend
```

Crea el archivo `.env`:

```env
# Configuración de Base de Datos
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/smartroute

# Configuración de RabbitMQ
RABBITMQ_URL=amqp://user:pass@rabbitmq:5672/
WEATHER_QUEUE=weather
TOURISM_QUEUE=tourism

# API Keys - REEMPLAZAR CON TUS CLAVES REALES
WEATHER_API=tu_api_key_openweathermap_aqui
API_KEY_PLACES=tu_api_key_google_places_aqui

# Azure OpenAI (opcional)
AZURE_API_KEY=tu_azure_api_key_aqui
AZURE_OPENAI_DEPLOYMENT=nombre_del_modelo_deployment
AZURE_ENDPOINT=https://tu-recurso.openai.azure.com/

# Configuración de Ollama (si usas modelos locales)
OLLAMA_BASE_URL=http://ollama:11434
```

⚠️ **IMPORTANTE**: Reemplaza los valores `tu_api_key_*` con tus claves reales.

### Paso 3: Verificar Docker Compose

Asegúrate de estar en la raíz del proyecto y verifica que el archivo `docker-compose.yml` existe:

```bash
cd ..  # Volver a la raíz si estás en backend/
ls docker-compose.yml
```

---

## Instalación y Ejecución

### Opción 1: Ejecución Completa con Docker (Recomendado)

#### Paso 1: Construir y Levantar los Servicios

Desde la raíz del proyecto, ejecuta:

```bash
docker compose up -d --build
```

Este comando:
- Construye las imágenes de Docker para backend y frontend
- Descarga las imágenes de PostgreSQL, RabbitMQ, Traefik y Ollama
- Inicia todos los contenedores en segundo plano

⏱️ **Tiempo estimado**: 5-10 minutos la primera vez (dependiendo de tu conexión)

#### Paso 2: Verificar el Estado de los Contenedores

```bash
docker compose ps
```

Deberías ver 6 servicios ejecutándose:
- `traefik`
- `postgres`
- `rabbitmq`
- `backend`
- `frontend`
- `ollamaSmartRoute`

#### Paso 3: Descargar el Modelo Ollama

Entra al contenedor de Ollama:

```bash
docker exec -it ollamaSmartRoute bash
```

Dentro del contenedor, descarga el modelo `llama3.1`:

```bash
ollama pull llama3.1
```

⏱️ **Tiempo estimado**: 5-15 minutos (el modelo pesa ~4.7GB)

Para verificar que el modelo se descargó correctamente:

```bash
ollama list
```

Sal del contenedor:

```bash
exit
```

#### Paso 4: Verificar los Servicios

Comprueba que todos los servicios están funcionando:

**Health Check del Backend:**
```bash
curl http://api.localhost/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "postgres": "Todo bien PostgreSQL",
  "rabbitmq": "Todo bien RabbitMQ"
}
```

**Acceso a los Servicios:**

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://app.localhost | Interfaz de usuario principal |
| **Backend API** | http://api.localhost | API REST y documentación |
| **Documentación API** | http://api.localhost/docs | Swagger UI interactivo |
| **RabbitMQ Management** | http://rabbitmq.localhost | Panel de gestión de colas |
| **Traefik Dashboard** | http://localhost:8081 | Panel de Traefik |
| **Ollama API** | http://ollama.localhost | API de Ollama |

**Credenciales RabbitMQ:**
- Usuario: `user`
- Contraseña: `pass`

---

### Opción 2: Desarrollo Local (Sin Docker)

Si prefieres ejecutar los servicios localmente para desarrollo:

#### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

#### Frontend

```bash
cd frontend

# Instalar dependencias (con npm)
npm install

# O con bun (más rápido)
bun install

# Ejecutar en modo desarrollo
npm run dev
# O con bun
bun run dev
```

**Nota**: Para desarrollo local necesitarás PostgreSQL y RabbitMQ corriendo localmente o ajustar las URLs de conexión.

---

## Estructura del Proyecto

```
SmartRoute/
├── backend/                        # Servicio Backend
│   ├── main.py                     # Punto de entrada de FastAPI
│   ├── routes.py                   # Definición de rutas/endpoints
│   ├── models.py                   # Modelos Pydantic
│   ├── connections.py              # Gestión de conexiones (DB, RabbitMQ)
│   ├── api_services.py             # Servicios y helpers de API
│   ├── langchain.py                # Integración con LangChain
│   ├── requirements.txt            # Dependencias de Python
│   ├── Dockerfile                  # Imagen Docker del backend
│   ├── .env                        # Variables de entorno (crear este)
│   ├── tourism_agent/              # Agente de Turismo
│   │   ├── tourism_agent.py        # Lógica del agente
│   │   ├── tourism_tools.py        # Herramientas del agente
│   │   ├── places_api.py           # Cliente de Google Places
│   │   └── categories.txt          # Categorías de lugares
│   └── weather_agent/              # Agente del Clima
│       ├── weather_agent.py        # Lógica del agente
│       ├── weather_api.py          # Cliente de OpenWeatherMap
│       └── json_structure.py       # Estructuras de datos
│
├── frontend/                       # Aplicación Frontend
│   ├── src/
│   │   ├── main.tsx                # Punto de entrada React
│   │   ├── App.tsx                 # Componente principal
│   │   ├── pages/                  # Páginas de la aplicación
│   │   │   ├── Index.tsx           # Página principal
│   │   │   └── NotFound.tsx        # Página 404
│   │   ├── components/             # Componentes reutilizables
│   │   │   ├── ItineraryForm.tsx   # Formulario de itinerario
│   │   │   ├── NavLink.tsx         # Componente de navegación
│   │   │   └── ui/                 # Componentes UI de Shadcn
│   │   ├── hooks/                  # Custom React Hooks
│   │   ├── lib/                    # Utilidades y helpers
│   │   └── assets/                 # Imágenes y recursos
│   ├── package.json                # Dependencias de Node
│   ├── vite.config.ts              # Configuración de Vite
│   ├── tailwind.config.ts          # Configuración de Tailwind
│   └── Dockerfile                  # Imagen Docker del frontend
│
├── database/
│   └── init.sql                    # Script de inicialización de BD
│
├── docker-compose.yml              # Orquestación de servicios
├── package.json                    # Configuración raíz del proyecto
└── README.md                       # Este archivo
```

---

## APIs y Endpoints

### Backend API Endpoints

La documentación completa e interactiva está disponible en: **http://api.localhost/docs**

#### Health Check

```http
GET /health
```

Verifica el estado del sistema y las conexiones.

**Respuesta:**
```json
{
  "status": "healthy",
  "postgres": "Todo bien PostgreSQL",
  "rabbitmq": "Todo bien RabbitMQ"
}
```

#### Recomendaciones de Viaje

```http
POST /api/travel-recommendations
Content-Type: application/json

{
  "prompt": "Quiero viajar a París por 5 días"
}
```

**Respuesta:**
```json
{
  "destination": "París, Francia",
  "weather": "Temperatura promedio: 18°C, Parcialmente nublado",
  "activities": [
    "Visitar la Torre Eiffel",
    "Recorrer el Museo del Louvre",
    "Pasear por los Campos Elíseos"
  ],
  "hotels": [
    "Hotel Le Marais",
    "Ibis Paris Centre"
  ]
}
```

#### Generar Itinerario Completo

```http
POST /generar-itinerario
Content-Type: application/json

{
  "city": "Barcelona",
  "time": "7 días"
}
```

#### Endpoints de Testing

```http
POST /send-message          # Enviar mensaje a RabbitMQ
POST /weather-agent         # Consultar agente del clima
POST /tourism-agent         # Consultar agente de turismo
```

---

## Base de Datos

### Esquema de Base de Datos

El script de inicialización (`database/init.sql`) crea las siguientes tablas:

#### Tabla `users`
Almacena información de los usuarios del sistema.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla `itineraries`
Almacena los itinerarios generados.

```sql
CREATE TABLE itineraries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    destination VARCHAR(150) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    weather_summary TEXT,
    itinerary_details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla `weather`
Almacena datos climáticos históricos.

```sql
CREATE TABLE weather (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    itinerary_id UUID REFERENCES itineraries(id) ON DELETE CASCADE,
    temperature NUMERIC(5,2),
    description VARCHAR(255),
    forecast JSONB,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla `destinations`
Almacena destinos específicos dentro de un itinerario.

```sql
CREATE TABLE destinations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    itinerary_id UUID REFERENCES itineraries(id) ON DELETE CASCADE,
    city VARCHAR(100),
    country VARCHAR(100),
    activities JSONB,
    estimated_weather VARCHAR(255),
    order_index INTEGER DEFAULT 1
);
```

#### Tabla `prompts`
Almacena el historial de consultas de usuarios.

```sql
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    city VARCHAR(100) NOT NULL,
    time_str VARCHAR(50) NOT NULL,
    response_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Acceso a PostgreSQL

Para conectarte directamente a la base de datos:

```bash
# Desde el host
docker exec -it smartroute-postgres-1 psql -U postgres -d smartroute

# O usando un cliente externo
Host: localhost
Port: 5433
Database: smartroute
User: postgres
Password: postgres
```

### Usuario de Prueba

El sistema incluye un usuario de prueba pre-creado:

```sql
INSERT INTO users (id, name, email)
VALUES ('00000000-0000-0000-0000-000000000001', 'testuser', 'testuser@example.com');
```

---

## 🔧 Troubleshooting

### Problema: Los contenedores no inician

**Solución:**

```bash
# Detener todos los contenedores
docker compose down

# Limpiar volúmenes (⚠️ esto borrará los datos)
docker compose down -v

# Reconstruir e iniciar
docker compose up -d --build
```

### Problema: Error de conexión a PostgreSQL

**Solución:**

Espera unos segundos para que PostgreSQL termine de inicializar:

```bash
# Ver logs de PostgreSQL
docker compose logs postgres

# Espera a ver: "database system is ready to accept connections"
```

### Problema: Frontend no carga

**Solución:**

```bash
# Ver logs del frontend
docker compose logs frontend

# Reiniciar solo el frontend
docker compose restart frontend
```

### Problema: Ollama no responde o es muy lento

**Solución:**

1. Verifica que el modelo esté descargado:
```bash
docker exec -it ollamaSmartRoute ollama list
```

2. Si tienes GPU, verifica que Docker tenga acceso:
```bash
# Debe mostrar tu GPU
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

3. Si no tienes GPU, Ollama usará CPU (será más lento):
```bash
# Monitorear uso de CPU
docker stats ollamaSmartRoute
```

### Problema: RabbitMQ no conecta

**Solución:**

```bash
# Ver logs de RabbitMQ
docker compose logs rabbitmq

# Reiniciar RabbitMQ
docker compose restart rabbitmq
```

### Problema: Traefik no redirige correctamente

**Solución:**

Asegúrate de que los dominios `.localhost` estén en tu archivo `hosts`:

**Windows**: `C:\Windows\System32\drivers\etc\hosts`  
**Linux/Mac**: `/etc/hosts`

Agrega:
```
127.0.0.1 api.localhost
127.0.0.1 app.localhost
127.0.0.1 rabbitmq.localhost
127.0.0.1 ollama.localhost
```

### Ver Logs de Todos los Servicios

```bash
# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend
docker compose logs -f frontend
```

### Monitorear Uso de GPU (si aplica)

```bash
# Desde el host
watch -n 1 nvidia-smi

# Desde el contenedor de Ollama
docker exec -it ollamaSmartRoute watch -n 1 nvidia-smi
```

---

## Pruebas

### Probar el Backend

```bash
# Health check
curl http://api.localhost/health

# Consulta al agente del clima
curl -X POST http://api.localhost/weather-agent \
  -H "Content-Type: application/json" \
  -d '{"city": "Bogotá", "time": "7"}'

# Consulta al agente de turismo
curl -X POST http://api.localhost/tourism-agent \
  -H "Content-Type: application/json" \
  -d '{"city": "Cartagena", "time": "3"}'
```

### Probar RabbitMQ

1. Accede a la interfaz de gestión: http://rabbitmq.localhost
2. Usuario: `user`, Contraseña: `pass`
3. Ve a la pestaña "Queues" para ver las colas activas

---

## Despliegue en Producción

### Consideraciones

1. **Variables de Entorno**: Usa secretos seguros, no valores hardcodeados
2. **Dominio Real**: Reemplaza `.localhost` con tu dominio real en Traefik
3. **HTTPS**: Configura certificados SSL (Let's Encrypt con Traefik)
4. **Base de Datos**: Usa una instancia de PostgreSQL gestionada (AWS RDS, Azure Database)
5. **Escalabilidad**: Usa Docker Swarm o Kubernetes para orquestación avanzada
6. **Monitoring**: Implementa Prometheus + Grafana para monitoreo
7. **Logs**: Centraliza logs con ELK Stack o similar

### Comandos de Despliegue

```bash
# Construir para producción
docker compose -f docker-compose.prod.yml up -d --build

# Ver estado
docker compose -f docker-compose.prod.yml ps

# Backup de base de datos
docker exec smartroute-postgres-1 pg_dump -U postgres smartroute > backup.sql
```

---

## Monitoreo y Métricas

### Endpoints de Monitoreo

- **Traefik Dashboard**: http://localhost:8081
- **RabbitMQ Metrics**: http://rabbitmq.localhost/api/overview
- **Backend Health**: http://api.localhost/health

### Métricas Clave

- Tiempo de respuesta de endpoints
- Cola de mensajes en RabbitMQ
- Uso de conexiones en PostgreSQL
- Uso de GPU/CPU en Ollama
- Tasa de errores en logs

---

## Recursos Adicionales

### Documentación Oficial

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://python.langchain.com/)
- [CrewAI](https://docs.crewai.com/)
- [Ollama](https://ollama.ai/docs)
- [React](https://react.dev/)
- [Shadcn/ui](https://ui.shadcn.com/)
- [Docker](https://docs.docker.com/)
- [Traefik](https://doc.traefik.io/traefik/)

### APIs Externas

- [OpenWeatherMap API](https://openweathermap.org/api)
- [Google Places API](https://developers.google.com/maps/documentation/places/web-service)

---

