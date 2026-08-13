import { useMemo, useState } from "react";

import "./FactoryLayout.css";


const HEAT_MODES = [
  {
    id: "overall",
    label: "Genel Durum",
  },
  {
    id: "temperature",
    label: "Sıcaklık",
  },
  {
    id: "vibration",
    label: "Titreşim",
  },
];


function getMachineStatus(
  machineId,
  mode,
  diagnosticsByMachine
) {
  const diagnostics =
    diagnosticsByMachine?.[machineId];

  if (!diagnostics) {
    return "unknown";
  }

  const thresholdAnalysis =
    diagnostics.threshold_analysis;

  if (!thresholdAnalysis) {
    return "unknown";
  }

  if (mode === "overall") {
    return (
      thresholdAnalysis.overall_status ||
      "unknown"
    );
  }

  const sensorKey =
    mode === "temperature"
      ? "temperature_c"
      : "vibration_mm_s";

  const sensorAnalysis =
    thresholdAnalysis.sensor_analysis || [];

  const sensorResult =
    Array.isArray(sensorAnalysis)
      ? sensorAnalysis.find(
          (item) =>
            item.sensor === sensorKey
        )
      : sensorAnalysis?.[sensorKey];

  const status =
    sensorResult?.status;

  if (
    status === "normal" ||
    status === "warning" ||
    status === "critical"
  ) {
    return status;
  }

  return "unknown";
}

function getStatusLabel(status) {
  const labels = {
    normal: "Normal",
    warning: "Uyarı",
    critical: "Kritik",
    unknown: "Bilinmiyor",
  };

  return labels[status] || "Bilinmiyor";
}


export default function FactoryLayout({
  hierarchy,
  diagnosticsByMachine,
  selectedMachineId,
  onSelectMachine,
  loading = false,
}) {
  const [heatMode, setHeatMode] =
    useState("overall");

  const machines = useMemo(() => {
    if (!hierarchy?.stations) {
      return [];
    }

    return hierarchy.stations.flatMap(
      (station) =>
        (station.machines || []).map(
          (machine) => ({
            ...machine,
            stationId: station.id,
            stationName: station.name,
          })
        )
    );
  }, [hierarchy]);

  const positionedMachines =
    machines.filter(
      (machine) =>
        machine.spatial?.x_pct != null &&
        machine.spatial?.y_pct != null
    );

  return (
    <section className="factory-layout-card">
      <div className="factory-layout-header">
        <div>
          <p className="factory-layout-eyebrow">
            FABRİKA GÖRÜNÜMÜ
          </p>

          <h2>Makine Durum Haritası</h2>

          <p className="factory-layout-description">
            Makinelerin fabrika yerleşimi
            üzerindeki anlık durumlarını
            görüntüleyin.
          </p>
        </div>

        <div className="heat-mode-selector">
          {HEAT_MODES.map((mode) => (
            <button
              key={mode.id}
              type="button"
              className={
                heatMode === mode.id
                  ? "heat-mode-button active"
                  : "heat-mode-button"
              }
              onClick={() =>
                setHeatMode(mode.id)
              }
            >
              {mode.label}
            </button>
          ))}
        </div>
      </div>

      <div className="factory-layout-legend">
        <span>
          <i className="legend-dot normal" />
          Normal
        </span>

        <span>
          <i className="legend-dot warning" />
          Uyarı
        </span>

        <span>
          <i className="legend-dot critical" />
          Kritik
        </span>

        <span>
          <i className="legend-dot unknown" />
          Veri yok
        </span>
      </div>

      <div className="factory-layout-canvas">
        <img
          src="/factory-layout.svg"
          alt="Fabrika yerleşim planı"
          className="factory-layout-image"
        />

        {positionedMachines.map(
          (machine) => {
            const status =
              getMachineStatus(
                machine.id,
                heatMode,
                diagnosticsByMachine
              );

            const isSelected =
              machine.id ===
              selectedMachineId;

            return (
              <button
                key={machine.id}
                type="button"
                className={[
                  "machine-marker",
                  `status-${status}`,
                  isSelected
                    ? "selected"
                    : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                style={{
                  left: `${machine.spatial.x_pct}%`,
                  top: `${machine.spatial.y_pct}%`,
                }}
                onClick={() =>
                  onSelectMachine(
                    machine.id
                  )
                }
                title={`${machine.name} • ${getStatusLabel(
                  status
                )}`}
              >
                <span className="machine-marker-pulse" />

                <span className="machine-marker-core" />

                <span className="machine-marker-label">
                  <strong>
                    {machine.name}
                  </strong>

                  <small>
                    {getStatusLabel(
                      status
                    )}
                  </small>
                </span>
              </button>
            );
          }
        )}

        {loading && (
          <div className="factory-layout-loading">
            Makine durumları
            yükleniyor...
          </div>
        )}
      </div>

      {positionedMachines.length === 0 && (
        <p className="factory-layout-empty">
          Layout üzerinde konumu
          tanımlanmış makine bulunamadı.
        </p>
      )}
    </section>
  );
}