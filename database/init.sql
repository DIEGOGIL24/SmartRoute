CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


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


CREATE TABLE weather (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    itinerary_id UUID REFERENCES itineraries(id) ON DELETE CASCADE,
    temperature NUMERIC(5,2),
    description VARCHAR(255),
    forecast JSONB,  
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE destinations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    itinerary_id UUID REFERENCES itineraries(id) ON DELETE CASCADE,
    city VARCHAR(100),
    country VARCHAR(100),
    activities JSONB,  
    estimated_weather VARCHAR(255),
    order_index INTEGER DEFAULT 1
);

CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    city VARCHAR(100) NOT NULL,
    time_str VARCHAR(50) NOT NULL,
    response_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX idx_itineraries_user ON itineraries(user_id);
CREATE INDEX idx_weather_itinerary ON weather(itinerary_id);
CREATE INDEX idx_destinations_itinerary ON destinations(itinerary_id);


CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_itinerary
BEFORE UPDATE ON itineraries
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();


CREATE VIEW full_itinerary_view AS
SELECT 
    i.id AS itinerary_id,
    u.name AS user_name,
    i.destination,
    i.start_date,
    i.end_date,
    i.weather_summary,
    i.itinerary_details,
    w.temperature,
    w.description AS current_weather,
    i.created_at
FROM itineraries i
JOIN users u ON i.user_id = u.id
LEFT JOIN weather w ON w.itinerary_id = i.id;

INSERT INTO users (id, name, email)
VALUES ('00000000-0000-0000-0000-000000000001', 'testuser', 'testuser@example.com');
