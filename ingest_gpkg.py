# Data_Ingestion\ingest_gpkg.py
import geopandas as gpd
from sqlalchemy import create_engine
import time
import warnings

warnings.filterwarnings('ignore')

# IMPORTANT: Update 'yourpassword' to your local PostgreSQL password
DB_URI = "postgresql://postgres:yourpassword@localhost:5432/ner_routing"
engine = create_engine(DB_URI)

# Targeting the specific dataset verified on your machine
GPKG_PATH = r"C:\Krish\SIH\Database\north-eastern-zone-260909-free.gpkg"

def ingest_network():
    start_time = time.time()
    print("[SYSTEM] Accessing GeoPackage: North-Eastern Zone")
    
    gdf = gpd.read_file(GPKG_PATH, layer='lines', engine='pyogrio')
    
    print("[SYSTEM] Filtering non-routable geometries...")
    network_edges = gdf[gdf['highway'].notna()].copy()
    
    print(f"[SYSTEM] Identified {len(network_edges)} routable edges. Pushing to PostGIS...")
    network_edges.to_postgis("road_network", engine, if_exists="replace", index=False)
    
    elapsed = round(time.time() - start_time, 2)
    print(f"[SYSTEM] Ingestion complete in {elapsed} seconds.")

if __name__ == "__main__":
    ingest_network()