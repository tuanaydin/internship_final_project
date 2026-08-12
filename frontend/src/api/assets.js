const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


async function fetchJson(url) {
  const response = await fetch(url);

  if (!response.ok) {
    let message = "Varlık bilgileri alınamadı.";

    try {
      const error = await response.json();

      if (error.detail) {
        message = error.detail;
      }
    } catch {
      // JSON olmayan hata cevabında
      // varsayılan mesaj kullanılır.
    }

    throw new Error(message);
  }

  return response.json();
}


export function getPlant(plantId) {
  return fetchJson(
    `${API_BASE_URL}/api/v1/plants/${plantId}`
  );
}


export function getStations(plantId) {
  return fetchJson(
    `${API_BASE_URL}/api/v1/plants/${plantId}/stations`
  );
}


export function getMachines(stationId) {
  return fetchJson(
    `${API_BASE_URL}/api/v1/stations/${stationId}/machines`
  );
}