-- Spatial_Database\create_topology.sql
ALTER TABLE road_network ADD COLUMN source INTEGER;
ALTER TABLE road_network ADD COLUMN target INTEGER;
ALTER TABLE road_network ADD COLUMN cost_len DOUBLE PRECISION;

-- Convert geometry lengths to accurate meters
UPDATE road_network 
SET cost_len = ST_Length(ST_Transform(geom, 3857));

-- Build the routing node map
SELECT pgr_createTopology('road_network', 0.00001, 'geom', 'osm_id');

-- Index for high-speed API querying
CREATE INDEX idx_road_network_source ON road_network(source);
CREATE INDEX idx_road_network_target ON road_network(target);