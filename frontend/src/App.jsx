import { useState } from "react";
import ReactMarkdown from "react-markdown";

import { askAssistant } from "./api/assistant";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { getMeasurementsAt } from "./api/measurements";


const DEFAULT_QUESTION =
  "Motor-A neden kritik durumda ve hangi bakım işlemleri yapılmalı?";


const TREND_LABELS = {
  increasing: "Artıyor",
  decreasing: "Azalıyor",
  stable: "Stabil",
};


const STATUS_LABELS = {
  critical: "Kritik",
  warning: "Uyarı",
  normal: "Normal",
};


const DIAGNOSIS_LABELS = {
  bearing_degradation: "Rulman Bozulması",
  cooling_degradation: "Soğutma Problemi",
  overload: "Aşırı Yük",
};

const SENSOR_CHARTS = {
  temperature: {
    label: "Sıcaklık",
    code: "TEMP",
    dataKey: "temperature",
    unit: "°C",
    axisDecimals: 0,
    valueDecimals: 2,
    padding: 2,
  },

  vibration: {
    label: "Titreşim",
    code: "VIB",
    dataKey: "vibration",
    unit: "mm/s",
    axisDecimals: 1,
    valueDecimals: 3,
    padding: 0.5,
  },

  current: {
    label: "Akım",
    code: "CUR",
    dataKey: "current",
    unit: "A",
    axisDecimals: 1,
    valueDecimals: 2,
    padding: 1,
  },

  load: {
    label: "Yük",
    code: "LOAD",
    dataKey: "load",
    unit: "%",
    axisDecimals: 0,
    valueDecimals: 2,
    padding: 5,
  },

  power: {
    label: "Güç",
    code: "PWR",
    dataKey: "power",
    unit: "kW",
    axisDecimals: 1,
    valueDecimals: 3,
    padding: 1,
  },
};

function toBackendTimestamp(value) {
  if (!value) {
    return "";
  }

  return `${value.replace("T", " ")}:00`;
}


function StatusBadge({ status }) {
  return (
    <span className={`status-badge status-${status}`}>
      {STATUS_LABELS[status] || status || "Bilinmiyor"}
    </span>
  );
}

function getAssetStatusClass(status) {
  if (!status) {
    return "unknown-dot";
  }

  if (status === "critical") {
    return "critical-dot";
  }

  if (status === "warning") {
    return "warning-dot";
  }

  return "normal-dot";
}

function MetricCard({
  title,
  value,
  unit,
  trend,
  code,
}) {
  return (
    <article className="metric-card">

      <div className="metric-card-header">
        <span className="metric-code">
          {code}
        </span>

        {trend && (
          <span className={`trend-pill trend-${trend}`}>
            <span className="trend-symbol">
              {trend === "increasing"
                ? "↗"
                : trend === "decreasing"
                  ? "↘"
                  : "→"}
            </span>

            {TREND_LABELS[trend] || trend}
          </span>
        )}
      </div>


      <span className="metric-title">
        {title}
      </span>


      <div className="metric-value-row">
        <strong className="metric-value">
          {value ?? "-"}
        </strong>

        {unit && (
          <span className="metric-unit">
            {unit}
          </span>
        )}
      </div>

    </article>
  );
}


function SourceCard({ source }) {
  return (
    <article className="source-card">
      <div className="source-header">
        <strong>
          {source.document_id || "Doküman"}
        </strong>

        <span className="source-type">
          {source.document_type || "-"}
        </span>
      </div>

      <code className="source-chunk">
        {source.chunk_id || "-"}
      </code>

      <small className="source-file">
        {source.source || "-"}
      </small>

      {source.page_number !== null &&
        source.page_number !== undefined && (
          <small>
            Sayfa: {source.page_number}
          </small>
        )}
    </article>
  );
}


function App() {
  const [machineId, setMachineId] =
    useState("MOTOR_A");

  const [timestamp, setTimestamp] =
    useState("2026-07-27T20:00");

  const [windowMinutes, setWindowMinutes] =
    useState(300);

  const [question, setQuestion] =
    useState(DEFAULT_QUESTION);

  const [result, setResult] =
    useState(null);

  const [measurements, setMeasurements] =
  useState([]);

  const [selectedSensor, setSelectedSensor] =
  useState("temperature");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  async function handleSubmit(event) {
    event.preventDefault();

    if (!question.trim()) {
      setError(
        "Lütfen bakım asistanına bir soru yazın."
      );
      return;
    }

    setLoading(true);
    setError("");

    try {
      const backendTimestamp =
  toBackendTimestamp(timestamp);

const [
  assistantResponse,
  measurementsResponse,
] = await Promise.all([
  askAssistant({
    machineId,
    question: question.trim(),
    timestamp: backendTimestamp,
    windowMinutes: Number(windowMinutes),
    topK: 5,
  }),

  getMeasurementsAt({
    machineId,
    timestamp: backendTimestamp,
    windowMinutes: Number(windowMinutes),
  }),
]);

setResult(assistantResponse);

setMeasurements(
  measurementsResponse.measurements || []
);
    } catch (err) {
      setError(
        err.message ||
          "Beklenmeyen bir hata oluştu."
      );
    } finally {
      setLoading(false);
    }
  }


  const deterministic =
    result?.deterministic_analysis;

  const evidence =
    deterministic?.evidence || {};

  const sources =
    result?.sources || [];


  const chartData = measurements.map((measurement) => ({
    time:
      measurement.timestamp?.slice(11, 16) ||
      "",

    temperature:
      measurement.temperature_c,

    vibration:
      measurement.vibration_mm_s,
          current:
      measurement.current_a,

    load:
      measurement.load_pct,

    power:
      measurement.power_kw,
  })
);

const activeSensor =
  SENSOR_CHARTS[selectedSensor];

const latestChartPoint =
  chartData.length > 0
    ? chartData[chartData.length - 1]
    : null;

const activeSensorValue =
  latestChartPoint?.[activeSensor.dataKey];


  return (
    <div className="app-shell">

    <aside className="sidebar">

  <div>
    <div className="brand">
      <div className="brand-mark">
        <span>IM</span>
      </div>

      <div className="brand-copy">
        <strong>
          IoT Maintenance
        </strong>

        <span>
          Decision Support
        </span>
      </div>
    </div>


    <nav className="main-navigation">

      <div className="nav-group">
        <p className="nav-group-title">
          GENEL
        </p>

        <button
          type="button"
          className="nav-item active"
        >
          <span className="nav-icon">
            ◫
          </span>

          Dashboard
        </button>
      </div>


      <div className="nav-group">
        <p className="nav-group-title">
          İZLEME
        </p>

        <button
          type="button"
          className="nav-item"
        >
          <span className="nav-icon">
            ◉
          </span>

          Varlıklar
        </button>

        <button
          type="button"
          className="nav-item"
        >
          <span className="nav-icon">
            △
          </span>

          Alarmlar

          {deterministic?.active_alarms?.length > 0 && (
            <span className="nav-counter">
              {
                deterministic
                  .active_alarms
                  .length
              }
            </span>
          )}
        </button>
      </div>


      <div className="nav-group">
        <p className="nav-group-title">
          BAKIM
        </p>

        <button
          type="button"
          className="nav-item"
        >
          <span className="nav-icon">
            ✦
          </span>

          Bakım Asistanı
        </button>
      </div>


      <div className="nav-group">
        <p className="nav-group-title">
          GÖRSELLEŞTİRME
        </p>

        <button
          type="button"
          className="nav-item nav-item-disabled"
          disabled
        >
          <span className="nav-icon">
            ◇
          </span>

          Fabrika Layout

          <span className="coming-soon">
            Yakında
          </span>
        </button>
      </div>

    </nav>


    <div className="asset-section">

      <div className="asset-section-header">
        <p className="nav-group-title">
          VARLIK HİYERARŞİSİ
        </p>

        <span className="asset-count">
          1 Makine
        </span>
      </div>


      <div className="asset-tree">

        <div className="asset-row plant">
          <span className="asset-status-dot unknown-dot" />

          <div>
            <strong>
              PLANT_01
            </strong>

            <small>
              Demo Factory
            </small>
          </div>
        </div>


        <div className="tree-connector">
          <span />
        </div>


        <div className="asset-row station">
          <span className="asset-node-icon">
            S
          </span>

          <div>
            <strong>
              STATION_01
            </strong>

            <small>
              Production Station
            </small>
          </div>
        </div>


        <button
          type="button"
          className="asset-row machine active"
          onClick={() =>
            setMachineId("MOTOR_A")
          }
        >
          <span
            className={`asset-status-dot ${getAssetStatusClass(
    deterministic?.overall_status)
            }`}
          />

          <div>
            <strong>
              MOTOR_A
            </strong>

            <small>
              Electric Motor
            </small>
          </div>
        </button>


        <div className="asset-row station disabled-asset">
          <span className="asset-node-icon">
            S
          </span>

          <div>
            <strong>
              STATION_02
            </strong>

            <small>
              Makine bulunmuyor
            </small>
          </div>
        </div>

      </div>

    </div>
  </div>


  <div className="sidebar-footer">

    <div className="system-health">
      <span className="online-dot" />

      <div>
        <strong>
          Sistem Çevrimiçi
        </strong>

        <small>
          FastAPI + RAG
        </small>
      </div>
    </div>

  </div>

</aside>


      <main className="main-content">

<header className="page-header">

  <div>
    <div className="breadcrumbs">
      <span>
        PLANT_01
      </span>

      <span className="breadcrumb-separator">
        /
      </span>

      <span>
        STATION_01
      </span>

      <span className="breadcrumb-separator">
        /
      </span>

      <strong>
        MOTOR_A
      </strong>
    </div>


    <div className="machine-heading">
      <div>
        <p className="eyebrow">
          MAKİNE DETAYI
        </p>

        <h1>
          Motor A
        </h1>
      </div>


      {deterministic && (
        <StatusBadge
          status={
            deterministic.overall_status
          }
        />
      )}
    </div>


    <p className="page-description">
      Gerçek zamanlı sensör analizi,
      deterministik teşhis ve teknik
      doküman destekli bakım karar desteği
    </p>
  </div>


  <div className="header-actions">

    <div className="connection-status">
      <span className="online-dot" />

      API yapılandırıldı
    </div>

  </div>

</header>


        <section className="configuration-card">

          <div className="form-field">
            <label>
              Makine
            </label>

            <select
              value={machineId}
              onChange={(event) =>
                setMachineId(
                  event.target.value
                )
              }
            >
              <option value="MOTOR_A">
                MOTOR_A
              </option>
            </select>
          </div>


          <div className="form-field">
            <label>
              Analiz Zamanı
            </label>

            <input
              type="datetime-local"
              value={timestamp}
              onChange={(event) =>
                setTimestamp(
                  event.target.value
                )
              }
            />
          </div>


          <div className="form-field">
            <label>
              Trend Penceresi
            </label>

            <select
              value={windowMinutes}
              onChange={(event) =>
                setWindowMinutes(
                  event.target.value
                )
              }
            >
              <option value={60}>
                Son 60 dakika
              </option>

              <option value={180}>
                Son 180 dakika
              </option>

              <option value={300}>
                Son 300 dakika
              </option>
            </select>
          </div>

        </section>


        {!result && (
          <section className="empty-state">
            <div className="empty-icon">
              ◇
            </div>

            <h2>
              Analiz için hazır
            </h2>

            <p>
              Bir zaman seçip bakım asistanına
              soru gönderdiğinizde deterministik
              analiz ve RAG sonuçları burada
              görüntülenecek.
            </p>
          </section>
        )}


        {deterministic && (
          <>
            <section className="section-block">

              <div className="section-heading">
                <div>
                  <p className="eyebrow">
                    DETERMINİSTİK ANALİZ
                  </p>

                  <h2>
                    Makine Durumu
                  </h2>
                </div>

                <span className="data-quality">
                  Veri Kalitesi:{" "}
                  <strong>
                    {
                      deterministic
                        .data_quality_status
                    }
                  </strong>
                </span>
              </div>


              <div className="summary-grid">

                <article className="summary-card summary-card-diagnosis">

  <div className="summary-card-header">
    <span className="summary-type">
      TEŞHİS 
    </span>

    <span className="confidence-chip">
      {deterministic.confidence === "high"
        ? "Yüksek Güven"
        : deterministic.confidence || "-"}
    </span>
  </div>


  <strong className="summary-value">
    {DIAGNOSIS_LABELS[
      deterministic.diagnosis
    ] ||
      deterministic.diagnosis ||
      " Teşhis yok"}
  </strong>


  <code className="summary-code">
    {deterministic.diagnosis || "-"}
  </code>


  <div className="summary-footer">
    Deterministik çoklu sensör analizi
  </div>

</article>


                <article className="summary-card summary-card-procedure">

  <div className="summary-card-header">
    <span className="summary-type">
      BAKIM PROSEDÜRÜ
    </span>

    <span className="procedure-chip">
       Önerilen
    </span>
  </div>


  <strong className="procedure-code">
    {
      deterministic
        .recommended_procedure ||
      "-"
    }
  </strong>


  <p className="summary-description">
    Deterministik analiz sonucuna göre
    önerilen ilk bakım yönlendirmesi.
  </p>


  <div className="summary-footer">
    Teknik prosedür ile desteklenir
  </div>

</article>


                <article className="summary-card summary-card-escalation">

  <div className="summary-card-header">
    <span className="summary-type">
      ESKALASYON
    </span>

    <span
      className={
        deterministic.escalation_required
          ? "escalation-chip required"
          : "escalation-chip"
      }
    >
      {deterministic.escalation_required
        ? "Gerekli"
        : "Gerekli Değil"}
    </span>
  </div>


  <strong className="procedure-code">
    {deterministic
      .escalation_required
      ? deterministic
          .escalation_procedure
      : "-"}
  </strong>


  <p className="summary-description">
    {deterministic
      .escalation_required
      ? "Yetkili bakım personeli tarafından kritik inceleme gereklidir."
      : "Mevcut durumda ek eskalasyon gerekmiyor."}
  </p>


  <div className="summary-footer">
    İnsan onaylı bakım kararı
  </div>

</article>
              </div>


              <div className="metrics-grid">

                <MetricCard
                  title="Sıcaklık"
                  code="TEMP"
                  value={evidence.temperature_c}
                  unit="°C"
                  trend={evidence.temperature_trend}
                />

                <MetricCard
                  title="Titreşim"
                  code="VIB"
                  value={
                    evidence.vibration_mm_s
                  }
                  unit="mm/s"
                  trend={
                    evidence.vibration_trend
                  }
                />

                <MetricCard
                  title="Akım"
                  code="CUR"
                  value={
                    evidence.current_a
                  }
                  unit="A"
                  trend={
                    evidence.current_trend
                  }
                />

                <MetricCard
                  title="Yük"
                  code="LOAD"
                  value={
                    evidence.load_pct
                  }
                  unit="%"
                  trend={
                    evidence.load_trend
                  }
                />

                <MetricCard
                  title="Güç"
                  code="PWR"
                  value={
                    evidence.power_kw
                  }
                  unit="kW"
                  trend={
                    evidence.power_trend
                  }
                />

              </div>


              <div className="alarm-panel">

  <div className="alarm-panel-heading">

    <div className="alarm-icon">
      !
    </div>

    <div>
      <span className="card-label">
        AKTİF ALARMLAR
      </span>

      <strong>
        {deterministic.active_alarms?.length || 0}
        {" "}aktif alarm
      </strong>
    </div>

  </div>


  <div className="alarm-list">

    {deterministic
      .active_alarms
      ?.map((alarm) => (
        <code
          key={alarm}
          className="alarm-chip"
        >
          <span className="alarm-dot" />
          {alarm}
        </code>
      ))}

  </div>

</div>

            </section>
          </>
        )}


 {chartData.length > 0 && (
  <section className="section-block">

    <div className="section-heading">
      <div>
        <p className="eyebrow">
          SENSÖR TRENDLERİ
        </p>

        <h2>
          Zaman Serisi Analizi
        </h2>
      </div>

      <span className="chart-window-badge">
        Son {windowMinutes} dakika
      </span>
    </div>


    <article className="trend-chart-card">

      <div className="sensor-chart-selector">

        {Object.entries(SENSOR_CHARTS).map(
          ([key, sensor]) => (
            <button
              key={key}
              type="button"
              className={`sensor-chart-button ${
                selectedSensor === key
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setSelectedSensor(key)
              }
            >
              <span>
                {sensor.code}
              </span>

              {sensor.label}
            </button>
          )
        )}

      </div>


      <div className="trend-chart-header">

        <div>
          <span className="chart-sensor-code">
            {activeSensor.code}
          </span>

          <h3>
            {activeSensor.label}
          </h3>
        </div>


        <strong>
          {activeSensorValue !== null &&
          activeSensorValue !== undefined
            ? Number(
                activeSensorValue
              ).toFixed(
                activeSensor.valueDecimals
              )
            : "-"}{" "}
          {activeSensor.unit}
        </strong>

      </div>


      <div className="chart-container chart-container-large">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          <LineChart
            data={chartData}
            margin={{
              top: 10,
              right: 15,
              left: -5,
              bottom: 0,
            }}
          >

            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#eaecf0"
            />


            <XAxis
              dataKey="time"
              tick={{
                fontSize: 9,
                fill: "#98a2b3",
              }}
              axisLine={false}
              tickLine={false}
              minTickGap={35}
            />


            <YAxis
              tick={{
                fontSize: 9,
                fill: "#98a2b3",
              }}
              axisLine={false}
              tickLine={false}
              domain={[
                (dataMin) =>
                  dataMin -
                  activeSensor.padding,

                (dataMax) =>
                  dataMax +
                  activeSensor.padding,
              ]}
              tickFormatter={(value) =>
                activeSensor.axisDecimals === 0
                  ? Math.round(value)
                  : Number(value).toFixed(
                      activeSensor.axisDecimals
                    )
              }
            />


            <Tooltip
              labelFormatter={(label) =>
                `Saat: ${label}`
              }
              formatter={(value) => [
                `${Number(value).toFixed(
                  activeSensor.valueDecimals
                )} ${activeSensor.unit}`,
                activeSensor.label,
              ]}
            />


            <Line
              type="monotone"
              dataKey={activeSensor.dataKey}
              stroke="#1769e0"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
              animationDuration={350}
            />

          </LineChart>
        </ResponsiveContainer>

      </div>

    </article>

  </section>
)}





        <section className="assistant-card">

          <div className="assistant-heading">

  <div className="assistant-title-group">

    <div className="assistant-logo">
      ✦
    </div>

    <div>
      <p className="eyebrow">
        AI MAINTENANCE COPILOT
      </p>

      <h2>
        Bakım Asistanı
      </h2>

      <span className="assistant-subtitle">
        Sensör kanıtları ve teknik dokümanlarla
        desteklenen bakım karar desteği
      </span>
    </div>

  </div>


  <span className="grounded-badge">
    <span className="grounded-dot" />
    Evidence Grounded
  </span>

</div>


          <form
            className="question-form"
            onSubmit={handleSubmit}
          >

            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(
                  event.target.value
                )
              }
              placeholder="Motor-A hakkında bakım sorusu sorun..."
              rows={4}
            />

            <div className="question-footer">

              <span>
                Deterministik analiz ve teknik
                dokümanlar kullanılarak cevaplanır.
              </span>

              <button
                type="submit"
                disabled={loading}
              >
                {loading
                  ? "Analiz Ediliyor..."
                  : "Soruyu Gönder"}
              </button>

            </div>

          </form>


          {error && (
            <div className="error-message">
              {error}
            </div>
          )}


          {loading && (
            <div className="loading-panel">
              <div className="loader" />

              <div>
                <strong>
                  Analiz hazırlanıyor
                </strong>

                <span>
                  Sensör kanıtları değerlendiriliyor,
                  teknik dokümanlar aranıyor ve
                  cevap oluşturuluyor...
                </span>
              </div>
            </div>
          )}


          {result && !loading && (
            <div className="assistant-result">
              <div className="user-message">

             <div className="message-label">
              SİZ
         </div>

         <div className="user-message-content">
         {result.question}
         </div>

          </div>

              <article className="answer-card">

<div className="answer-header">

  <span className="answer-icon">
    AI
  </span>

  <div>
    <strong>
      Bakım Asistanı
    </strong>

    <small>
      Deterministik analiz + RAG
    </small>
  </div>

</div>


                <div className="markdown-content">
                  <ReactMarkdown>
                    {result.answer}
                  </ReactMarkdown>
                </div>

              </article>


              <section className="sources-panel">

                <div className="sources-heading">
                  <div>
                    <p className="eyebrow">
                      RETRIEVAL
                    </p>

                    <h3>
                      Getirilen Teknik Kaynaklar
                    </h3>
                  </div>

                  <span className="source-count">
                    {sources.length} chunk
                  </span>
                </div>


                <div className="sources-grid">
                  {sources.map(
                    (source) => (
                      <SourceCard
                        key={
                          source.chunk_id
                        }
                        source={source}
                      />
                    )
                  )}
                </div>

              </section>

            </div>
          )}

        </section>

      </main>

    </div>
  );
}


export default App;