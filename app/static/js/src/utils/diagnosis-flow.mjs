/** Keep provider status, time and source attached to the scan's weather context. */
export function weatherContext(response) {
  if (!['OK', 'SIMULATED'].includes(response?.status) || !response.result) return null;
  const r = response.result;
  return {
    status: response.status,
    source: response.sources?.[0]?.title || 'Unspecified source',
    source_url: response.sources?.[0]?.url || null,
    fetched_at_utc: r.fetched_at_utc,
    valid_from_utc: r.valid_from_utc,
    valid_to_utc: r.valid_to_utc,
    location: r.requested_location,
    summary: r.summary,
    advisory_actions: (r.alerts || []).map(alert => alert.action),
    limitations: response.limitations || [],
  };
}

export function scanLocation(mode, latitude, longitude) {
  if (mode === 'none') return null;
  // The demo has a stated example location; never silently substitute it for live coordinates.
  if (mode === 'demo') return { latitude: 18.5204, longitude: 73.8567 };
  if (mode !== 'live' || String(latitude).trim() === '' || String(longitude).trim() === '') {
    throw new Error('Enter your farm coordinates or choose “No weather”.');
  }
  const lat = Number(latitude), lon = Number(longitude);
  if (!Number.isFinite(lat) || !Number.isFinite(lon) || Math.abs(lat) > 90 || Math.abs(lon) > 180) {
    throw new Error('Enter a latitude from -90 to 90 and longitude from -180 to 180.');
  }
  return { latitude: lat, longitude: lon };
}
