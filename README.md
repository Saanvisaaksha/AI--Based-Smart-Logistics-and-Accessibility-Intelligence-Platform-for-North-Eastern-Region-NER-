# AI--Based-Smart-Logistics-and-Accessibility-Intelligence-Platform-for-North-Eastern-Region-NER-

# TopoRoute: AI-Based Smart Logistics and Accessibility Intelligence Platform for NER

TopoRoute is a terrain-aware logistics and accessibility intelligence platform engineered for the North Eastern Region (NER) of India. The platform integrates live topographical data, regional hazard risk indices, and open-source routing engines to compute safe and realistic travel paths across challenging mountain corridors.

---

Key Features

* **Terrain-Aware Routing:** Calculates distance, hill-adjusted travel times, and elevation constraints rather than relying solely on linear planar distance.
* **AI Safety Index:** Generates a deterministic 0–100 safety score for every route by evaluating slope elevation, rainfall/moisture telemetry, and historical hazard records.
* **NER Region Alert System:** Automatically flags active complex terrain warnings upon route dispatch.
* **Decoupled Architecture:** Built on an independent spatial database layer, a high-performance FastAPI microservice backend, and a lightweight web interface.
* **Multilingual Support:** Localized routing reports and navigation alerts supporting multiple languages (including English, Hindi, Bengali, Assamese, and others).
* **Offline Resilience & Fallback:** Employs spatial indexing and cached graph nodes to handle intermittent connectivity and route interruptions.

---

## System Architecture

```text
Data Ingestion Pipeline (One-Time Setup)
Geofabrik OSM Data / GeoPackage 
       │
       ▼
GeoPandas Filtering (Routable Edges)
       │
       ▼
PostGIS + pgRouting (Topology, Edge Length, Graph Costs)

Real-Time Request Pipeline
Client Request (Origin, Destination, Language)
       │
       ▼
FastAPI Service (/route/optimize)
       │
       ├──► OSRM Routing Engine (Primary / Backup Endpoint)
       │
       └──► Safety Index Engine (Hazard & Slope Evaluation)
       │
       ▼
JSON Payload Response (Coordinates, Duration, Distance, Safety Score)
       │
       ▼
Frontend UI (Leaflet Map, KPI Dashboard, Multilingual Display)

```

---

## Datasets and References

The platform leverages terrain data, hazard susceptibility models, and road network extracts:

* **OpenStreetMap (OSM) Road Network Extracts:** Regional boundary and highway shapefile extracts sourced from [Geofabrik India Regional Downloads](https://download.geofabrik.de/asia/india.html?utm_source=gemini).
* **Landslide Susceptibility & Risk Dataset:** Spatial hazard records sourced from [Zenodo Hazard Repository (Record 10085272)](https://zenodo.org/records/10085272?utm_source=gemini).
* **Landslide Susceptibility Modeling Research:** Methodology referencing [National-scale Landslide Susceptibility and Risk Mapping of India](https://www.google.com/search?q=https://www.researchgate.net/publication/399252003_Nationalscale_landslide_susceptibility_and_risk_mapping_of_India_using_a_hybrid_data-driven_approach&utm_source=gemini).
* **Regional Development & Connectivity Data:** Infrastructure analytics published by the [Ministry of Development of North Eastern Region (MDoNER Report 1)](https://www.google.com/search?q=https://www.mdoner.gov.in/static/uploads/2025/12/383b6f83405b0aebd9de94a3567b115b.pdf&utm_source=gemini) and [MDoNER Report 2](https://www.google.com/search?q=https://www.mdoner.gov.in/static/uploads/2025/12/5d73ce16d0bab90283676744455b53ba.pdf&utm_source=gemini).
* **Disaster Alert Infrastructure:** Architecture patterns based on [SACHET Mobile Early Disaster Alert Application](https://www.ijprems.com/ijprems-paper/sachet--a-mobile-based-early-disaster-alert-application?utm_source=gemini).
* **Localization Services:** Multilingual models referencing [Bhashini Translation Services](https://anuvaad.bhashini.gov.in/text-to-text-translation?utm_source=gemini).

---

## Directory Structure

```text
NER_Logistics_Platform/
├── Backend_Service/
│   └── src/
│       └── main.py              # FastAPI application and route optimization logic
├── Data_Ingestion/
│   └── ingest_gpkg.py           # GeoPackage parsing and PostGIS ingestion script
├── Frontend_Interface/
│   ├── index.html               # Web interface layout
│   ├── script.js                # Map rendering and API integration logic
│   └── style.css                # Interface styles and themes
└── Spatial_Database/
    ├── init_postgis.sql         # PostGIS and pgRouting extension initializations
    └── create_topology.sql      # Topology network generation scripts

```

---

## Prerequisites

* Python 3.10 or higher
* PostgreSQL with PostGIS and pgRouting extensions installed
* GDAL and GEOS native system libraries (required by GeoPandas and Fiona)

---

## Installation

### 1. Clone or Extract the Repository

Navigate to the project root directory:

```bash
cd NER_Logistics_Platform

```

### 2. Set Up a Python Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate on Linux / macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

```

### 3. Install Required Python Libraries

```bash
pip install --upgrade pip
pip install fastapi uvicorn pydantic requests psycopg2-binary sqlalchemy geopandas shapely fiona pyproj

```

---

## Database Setup and Data Ingestion

1. **Initialize Spatial Extensions:**
Run the initialization scripts inside PostgreSQL:
```bash
psql -U postgres -d your_database -f Spatial_Database/init_postgis.sql

```


2. **Ingest Spatial Road Networks:**
Execute the data ingestion script to load GeoPackage road networks into PostGIS:
```bash
python Data_Ingestion/ingest_gpkg.py

```


3. **Build Topology Graph:**
Build routing nodes and edge costs:
```bash
psql -U postgres -d your_database -f Spatial_Database/create_topology.sql

```



---

## Running the Backend Service

### Option 1: Standard Development Run (with Auto-Reload)

Navigate to the `Backend_Service` folder and launch the Uvicorn server:

```bash
cd Backend_Service
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

```

### Option 2: Running from the Project Root

```bash
uvicorn Backend_Service.src.main:app --host 127.0.0.1 --port 8000 --reload

```

### Option 3: Production Execution with Multiple Workers

```bash
cd Backend_Service
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4

```

---

## Verification and API Documentation

Once the backend service is running, access the interactive API documentation and test endpoints:

* **Swagger UI:** `http://localhost:8000/docs`
* **ReDoc:** `http://localhost:8000/redoc`
* **Health Check / Base Endpoint:** `http://localhost:8000/`

### Example Route Optimization Request

**Endpoint:** `POST /route/optimize`

**Payload:**

```json
{
  "origin": {
    "lat": 26.1445,
    "lon": 91.7362
  },
  "destination": {
    "lat": 25.5788,
    "lon": 91.8933
  },
  "language": "en"
}

```

---

## Running the Frontend Interface

To serve the frontend interface without cross-origin file restrictions, run a static HTTP server from the `Frontend_Interface` directory:

```bash
cd Frontend_Interface
python -m http.server 3000

```

Open `http://localhost:3000` in any modern web browser to view the interactive map and route analytics dashboard.
