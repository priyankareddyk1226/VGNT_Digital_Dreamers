import React, { useEffect, useRef } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export default function LandIntelligenceMap() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [hoverInfo, setHoverInfo] = React.useState<any>(null);

  const { data: geojsonData, isLoading, error } = useQuery({
    queryKey: ['parcels-gis'],
    queryFn: async () => {
      const response = await axios.get('/api/gis/parcels');
      return response.data;
    }
  });

  useEffect(() => {
    if (map.current || !mapContainer.current || !geojsonData) return; // initialize map only once
    
    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'osm': {
            type: 'raster',
            tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap Contributors'
          }
        },
        layers: [
          {
            id: 'osm',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 22
          }
        ]
      },
      center: [78.4, 17.4],
      zoom: 11
    });

    map.current.on('load', () => {
      if (!map.current) return;
      
      map.current.addSource('parcels', {
        type: 'geojson',
        data: geojsonData
      });

      map.current.addLayer({
        id: 'parcels-layer',
        type: 'fill',
        source: 'parcels',
        paint: {
          'fill-color': [
            'match',
            ['get', 'risk_level'],
            'CRITICAL', '#dc2626',
            'HIGH', '#f97316',
            'MEDIUM', '#eab308',
            'LOW', '#22c55e',
            '#cbd5e1'
          ],
          'fill-opacity': 0.6,
          'fill-outline-color': '#000000'
        }
      });

      map.current.on('mousemove', 'parcels-layer', (e) => {
        if (e.features && e.features.length > 0) {
          setHoverInfo({
            feature: e.features[0],
            x: e.point.x,
            y: e.point.y
          });
        }
      });

      map.current.on('mouseleave', 'parcels-layer', () => {
        setHoverInfo(null);
      });
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [geojsonData]);

  if (isLoading) return <div className="flex h-full items-center justify-center">Loading Spatial Data...</div>;
  if (error) return <div className="flex h-full items-center justify-center text-red-500">Error loading map data</div>;

  return (
    <div className="w-full h-full relative">
      <div ref={mapContainer} className="w-full h-full" />
      {/* Custom Tooltip */}
      {hoverInfo && (
        <div className="absolute bg-card text-card-foreground border border-border rounded shadow-lg p-3 pointer-events-none text-sm z-10" style={{left: hoverInfo.x + 15, top: hoverInfo.y + 15}}>
          <div className="font-bold border-b pb-1 mb-1">{hoverInfo.feature.properties.id}</div>
          <div>Survey: {hoverInfo.feature.properties.survey_number}</div>
          <div>Risk: {hoverInfo.feature.properties.risk_score.toFixed(1)} ({hoverInfo.feature.properties.risk_level})</div>
          <div className="text-muted-foreground">{hoverInfo.feature.properties.village}, {hoverInfo.feature.properties.district}</div>
        </div>
      )}
    </div>
  );
}
