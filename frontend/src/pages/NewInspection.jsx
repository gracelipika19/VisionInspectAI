import { useState } from "react";

import { inspectImage } from "../services/api";
import DetectionOverlay from "../components/DetectionOverlay";


function NewInspection() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  // ==================================================
  // Handle Image Selection
  // ==================================================

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    const allowedTypes = [
      "image/jpeg",
      "image/png",
    ];

    if (!allowedTypes.includes(file.type)) {
      setError("Please select a JPG or PNG image.");
      return;
    }

    // Clean up previous preview URL
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));

    setResult(null);
    setError("");
  };


  // ==================================================
  // Run Inspection
  // ==================================================

  const handleInspect = async () => {
    if (!selectedFile) {
      setError("Please select a PCB image first.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data = await inspectImage(selectedFile);

      setResult(data);

    } catch (err) {
      console.error(err);

      setError(
        err.response?.data?.detail ||
          "Inspection failed. Please check that the backend is running."
      );

    } finally {
      setLoading(false);
    }
  };


  // ==================================================
  // Reset Inspection
  // ==================================================

  const handleReset = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError("");
  };


  // ==================================================
  // Helper: Format Defect Name
  // ==================================================

  const formatDefectName = (name) => {
    return name
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  };


  // ==================================================
  // Helper: Quality Class
  // ==================================================

  const getSeverityClass = (severity) => {
    if (!severity) {
      return "";
    }

    return severity.toLowerCase();
  };


  const getDecisionClass = (decision) => {
    if (!decision) {
      return "";
    }

    return decision.toLowerCase();
  };


  return (
    <section className="inspection-page">

      {/* ==================================================
          Page Header
      ================================================== */}

      <div className="inspection-page-header">

        <div>

          <h2>
            New Inspection
          </h2>

          <p>
            Upload a PCB image to detect manufacturing
            defects using the YOLO inspection model.
          </p>

        </div>

      </div>


      {/* ==================================================
          Inspection Card
      ================================================== */}

      <section className="inspection-card">

        <div className="upload-section">

          {/* ==================================================
              Upload Area
          ================================================== */}

          <div className="upload-box">

            <div className="upload-icon">
              📷
            </div>

            <h3>
              Upload PCB Image
            </h3>

            <p>
              Select a JPG or PNG image for inspection.
            </p>


            <label className="file-button">

              Choose Image

              <input
                type="file"
                accept="image/jpeg,image/png"
                onChange={handleFileChange}
              />

            </label>


            {selectedFile && (

              <p className="file-name">
                Selected: {selectedFile.name}
              </p>

            )}

          </div>


          {/* ==================================================
              Image Preview / Inspection Result
          ================================================== */}

          {previewUrl && (

            <div className="preview-section">

              <h3>
                {result
                  ? "PCB Inspection Result"
                  : "Preview"}
              </h3>


              {result ? (

                <DetectionOverlay
                  imageUrl={previewUrl}
                  imageWidth={result.image_width}
                  imageHeight={result.image_height}
                  detections={result.detections}
                />

              ) : (

                <img
                  src={previewUrl}
                  alt="PCB preview"
                  className="preview-image"
                />

              )}

            </div>

          )}

        </div>


        {/* ==================================================
            Action Buttons
        ================================================== */}

        <div className="inspection-actions">

          <button
            className="inspect-button"
            onClick={handleInspect}
            disabled={!selectedFile || loading}
          >

            {loading
              ? "Inspecting..."
              : "Inspect PCB"}

          </button>


          {selectedFile && (

            <button
              className="reset-button"
              onClick={handleReset}
              disabled={loading}
            >
              Reset
            </button>

          )}

        </div>


        {/* ==================================================
            Error Message
        ================================================== */}

        {error && (

          <div className="error-message">
            {error}
          </div>

        )}

      </section>


      {/* ==================================================
          Inspection Result
      ================================================== */}

      {result && (

        <section className="result-card">

          {/* ==================================================
              Result Header
          ================================================== */}

          <div className="result-header">

            <div>

              <h2>
                Inspection Result
              </h2>

              <p>
                {result.filename}
              </p>

              <small>
                Inspection ID: #{result.inspection_id}
              </small>

            </div>


            <span
              className={`result-status ${
                result.status === "PASS"
                  ? "pass"
                  : "defective"
              }`}
            >
              {result.status}
            </span>

          </div>


          {/* ==================================================
              Quality Assessment
          ================================================== */}

          <div className="quality-section">

            <h3>
              Quality Assessment
            </h3>


            <div className="quality-grid">

              {/* Severity */}

              <div
                className={`quality-card severity-${getSeverityClass(
                  result.severity
                )}`}
              >

                <span>
                  Severity
                </span>

                <strong>
                  {result.severity}
                </strong>

              </div>


              {/* Risk */}

              <div
                className={`quality-card risk-${getSeverityClass(
                  result.risk
                )}`}
              >

                <span>
                  Risk
                </span>

                <strong>
                  {result.risk}
                </strong>

              </div>


              {/* Decision */}

              <div
                className={`quality-card decision-${getDecisionClass(
                  result.decision
                )}`}
              >

                <span>
                  Decision
                </span>

                <strong>
                  {result.decision.replaceAll(
                    "_",
                    " "
                  )}
                </strong>

              </div>

            </div>


            {/* Recommendation */}

            <div className="recommendation-box">

              <span>
                Recommendation
              </span>

              <strong>
                {result.recommendation}
              </strong>

            </div>

          </div>


          {/* ==================================================
              Result Statistics
          ================================================== */}

          <div className="result-stats">

            <div className="stat">

              <span>
                Defects Found
              </span>

              <strong>
                {result.defect_count}
              </strong>

            </div>


            <div className="stat">

              <span>
                Image Width
              </span>

              <strong>
                {result.image_width}px
              </strong>

            </div>


            <div className="stat">

              <span>
                Image Height
              </span>

              <strong>
                {result.image_height}px
              </strong>

            </div>


            <div className="stat">

              <span>
                Inspected By
              </span>

              <strong>
                {result.inspected_by}
              </strong>

            </div>

          </div>


          {/* ==================================================
              Detection List
          ================================================== */}

          <div className="detections">

            <h3>
              Detected Defects
            </h3>


            {result.detections.length === 0 ? (

              <p className="no-defects">
                No manufacturing defects detected.
              </p>

            ) : (

              <div className="detection-list">

                {result.detections.map(
                  (detection, index) => (

                    <div
                      className="detection"
                      key={index}
                    >

                      <div>

                        <strong>
                          {formatDefectName(
                            detection.class_name
                          )}
                        </strong>

                        <span>
                          Detection #{index + 1}
                        </span>

                      </div>


                      <strong>
                        {(
                          detection.confidence * 100
                        ).toFixed(2)}
                        %
                      </strong>

                    </div>

                  )
                )}

              </div>

            )}

          </div>

        </section>

      )}

    </section>
  );
}


export default NewInspection;