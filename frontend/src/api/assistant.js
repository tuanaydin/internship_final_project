const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


export async function askAssistant({
  machineId,
  question,
  timestamp,
  windowMinutes = 300,
  topK = 5,
}) {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/machines/${machineId}/assistant/ask`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        question,
        timestamp,
        window_minutes: windowMinutes,
        top_k: topK,
      }),
    }
  );

  if (!response.ok) {
    let message =
      "Bakım asistanı isteği başarısız oldu.";

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