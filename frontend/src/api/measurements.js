const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


export async function getMeasurementsAt({
  machineId,
  timestamp,
  windowMinutes,
}) {
  const params = new URLSearchParams({
    timestamp,
    window_minutes: String(windowMinutes),
  });

  const response = await fetch(
    `${API_BASE_URL}/api/v1/machines/${machineId}/measurements/at?${params}`
  );

  if (!response.ok) {
    let message =
      "Sensör geçmişi alınamadı.";

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