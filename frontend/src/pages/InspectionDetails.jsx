import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import api from "../services/api";


function InspectionDetails() {
  const { inspectionId } = useParams();

  const [inspection, setInspection] = useState(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");


  // ==================================================
  // Fetch Inspection Details
  // ==================================================

  useEffect(() => {
    const fetchInspection = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          `/inspections/${inspectionId}`
        );

        setInspection(response.data);

      } catch (err) {
        console.error(err);

        setError(
          err.response?.data?.detail ||
          "Unable to load inspection details."
        );

      } finally {
        setLoading(false);
      }
    };

    fetchInspection();
  }, [inspectionId]);


  // ==================================================
  // Loading
  // ==================================================

  if (loading) {
    return (
      <section className="details-page">

        <div className="details-message">
          Loading inspection details...
        </div>

      </section>
    );
  }


  // ==================================================
  // Error
  // ==================================================

  if (error) {
    return (
      <section className="details-page">

        <div className="details-error">
          {error}
        </div>

        <Link
          to="/history"
          className="back-button"
        >
          ← Back to History
        </Link>

      </section>
    );
  }


  // ==================================================
  // Safety Check
  // ==================================================

  if (!inspection) {
    return (
      <section className="details-page">

        <div className="details-error">
          Inspection not found.
        </div>

        <Link
          to="/history"
          className="back-button"
        >
          ← Back to History
        </Link>

      </section>
    );
  }


  // ==================================================
  // Helper
  // ==================================================

  const formatDefectName = (name) => {
    return name
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  };


  const formatDecision = (decision) => {
    if (!decision) {
      return "-";
    }

    return decision.replaceAll("_", " ");
  };


  // ==================================================
  // Inspection Details
  // ==================================================

  return (
    <section className="details-page">

      {/* ==================================================
          Header
      ================================================== */}

      <div className="details-header">

        <div>

          <Link
            to="/history"
            className="back-link"
          >
            ← Back to History
          </Link>

          <h2>
            Inspection #{inspection.inspection_id}
          </h2>

          <p>
            {inspection.filename}
          </p>

        </div>


        <span
          className={`details-status ${
            inspection.status === "PASS"
              ? "details-pass"
              : "details-defective"
          }`}
        >
          {inspection.status}
        </span>

      </div>


      {/* ==================================================
          Summary
      ================================================== */}

      <div className="details-summary">

        <div className="details-stat">

          <span>
            Defects Found
          </span>

          <strong>
            {inspection.defect_count}
          </strong>

        </div>


        <div className="details-stat">

          <span>
            Inspection ID
          </span>

          <strong>
            #{inspection.inspection_id}
          </strong>

        </div>


        <div className="details-stat">

          <span>
            Inspected At
          </span>

          <strong className="details-date">
            {new Date(
              inspection.inspected_at
            ).toLocaleString()}
          </strong>

        </div>

      </div>


      {/* ==================================================
          Quality Assessment
      ================================================== */}

      <div className="details-card">

        <div className="details-card-header">

          <div>

            <h3>
              Quality Assessment
            </h3>

            <p>
              Quality evaluation generated from
              the detected defect confidence levels.
            </p>

          </div>

        </div>


        <div className="details-quality-grid">

          {/* Severity */}

          <div
            className={`details-quality-item severity-${(
              inspection.severity || ""
            ).toLowerCase()}`}
          >

            <span>
              Severity
            </span>

            <strong>
              {inspection.severity || "-"}
            </strong>

          </div>


          {/* Risk */}

          <div
            className={`details-quality-item risk-${(
              inspection.risk || ""
            ).toLowerCase()}`}
          >

            <span>
              Risk
            </span>

            <strong>
              {inspection.risk || "-"}
            </strong>

          </div>


          {/* Decision */}

          <div className="details-quality-item">

            <span>
              Decision
            </span>

            <strong>
              {formatDecision(
                inspection.decision
              )}
            </strong>

          </div>

        </div>


        {/* Recommendation */}

        <div className="details-recommendation">

          <span>
            Recommendation
          </span>

          <strong>
            {inspection.recommendation || "-"}
          </strong>

        </div>

      </div>


      {/* ==================================================
          Detected Defects
      ================================================== */}

      <div className="details-card">

        <div className="details-card-header">

          <div>

            <h3>
              Detected Defects
            </h3>

            <p>
              YOLO model detections recorded during
              this inspection.
            </p>

          </div>

        </div>


        {inspection.detections.length === 0 ? (

          <div className="details-no-defects">

            <strong>
              No defects detected
            </strong>

            <span>
              This PCB passed the inspection.
            </span>

          </div>

        ) : (

          <div className="details-detection-list">

            {inspection.detections.map(
              (detection, index) => (

                <div
                  className="details-detection"
                  key={index}
                >

                  <div className="details-detection-info">

                    <strong>
                      {formatDefectName(
                        detection.class_name
                      )}
                    </strong>

                    <span>
                      Detection #{index + 1}
                    </span>

                  </div>


                  <div className="details-confidence">

                    {(
                      detection.confidence * 100
                    ).toFixed(2)}
                    %

                  </div>

                </div>

              )
            )}

          </div>

        )}

      </div>


      {/* ==================================================
          Bounding Box Coordinates
      ================================================== */}

      {inspection.detections.length > 0 && (

        <div className="details-card">

          <div className="details-card-header">

            <div>

              <h3>
                Detection Coordinates
              </h3>

              <p>
                Bounding-box coordinates returned by
                the YOLO model.
              </p>

            </div>

          </div>


          <div className="coordinates-wrapper">

            <table className="coordinates-table">

              <thead>

                <tr>

                  <th>
                    Detection
                  </th>

                  <th>
                    Class
                  </th>

                  <th>
                    Confidence
                  </th>

                  <th>
                    X1
                  </th>

                  <th>
                    Y1
                  </th>

                  <th>
                    X2
                  </th>

                  <th>
                    Y2
                  </th>

                </tr>

              </thead>


              <tbody>

                {inspection.detections.map(
                  (detection, index) => (

                    <tr key={index}>

                      <td>
                        #{index + 1}
                      </td>

                      <td>
                        {formatDefectName(
                          detection.class_name
                        )}
                      </td>

                      <td>
                        {(
                          detection.confidence * 100
                        ).toFixed(2)}
                        %
                      </td>

                      <td>
                        {detection.bbox[0]}
                      </td>

                      <td>
                        {detection.bbox[1]}
                      </td>

                      <td>
                        {detection.bbox[2]}
                      </td>

                      <td>
                        {detection.bbox[3]}
                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        </div>

      )}

    </section>
  );
}


export default InspectionDetails;