import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../services/api";


function History() {
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // ==================================================
  // Fetch Inspection History
  // ==================================================

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get("/inspections");

        setInspections(
          response.data.inspections || []
        );

      } catch (err) {
        console.error(err);

        setError(
          err.response?.data?.detail ||
          "Unable to load inspection history."
        );

      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);


  // ==================================================
  // Loading
  // ==================================================

  if (loading) {
    return (
      <section className="history-page">

        <div className="history-message">
          Loading inspection history...
        </div>

      </section>
    );
  }


  // ==================================================
  // Error
  // ==================================================

  if (error) {
    return (
      <section className="history-page">

        <div className="history-error">
          {error}
        </div>

      </section>
    );
  }


  // ==================================================
  // Helper Functions
  // ==================================================

  const formatDecision = (decision) => {
    if (!decision) {
      return "-";
    }

    return decision.replaceAll("_", " ");
  };


  const formatSeverity = (severity) => {
    if (!severity) {
      return "-";
    }

    return severity;
  };


  // ==================================================
  // History Page
  // ==================================================

  return (
    <section className="history-page">

      {/* ==================================================
          Page Header
      ================================================== */}

      <div className="history-header">

        <div>

          <h2>
            Inspection History
          </h2>

          <p>
            Review previous PCB inspection results.
          </p>

        </div>


        <div className="history-count">

          <span>
            Total Inspections
          </span>

          <strong>
            {inspections.length}
          </strong>

        </div>

      </div>


      {/* ==================================================
          Empty State
      ================================================== */}

      {inspections.length === 0 ? (

        <div className="history-empty">

          <h3>
            No inspections yet
          </h3>

          <p>
            Run your first PCB inspection to see
            the result here.
          </p>

          <Link
            to="/inspection"
            className="history-action"
          >
            Start Inspection
          </Link>

        </div>

      ) : (

        /* ==================================================
           Inspection Table
        ================================================== */

        <div className="history-card">

          <div className="history-table-wrapper">

            <table className="history-table">

              <thead>

                <tr>

                  <th>
                    ID
                  </th>

                  <th>
                    Filename
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                    Defects
                  </th>

                  <th>
                    Severity
                  </th>

                  <th>
                    Risk
                  </th>

                  <th>
                    Decision
                  </th>

                  <th>
                    Inspected At
                  </th>

                  <th>
                    Action
                  </th>

                </tr>

              </thead>


              <tbody>

                {inspections.map(
                  (inspection) => (

                    <tr
                      key={inspection.inspection_id}
                    >

                      {/* ID */}

                      <td>
                        #{inspection.inspection_id}
                      </td>


                      {/* Filename */}

                      <td className="history-filename">

                        {inspection.filename}

                      </td>


                      {/* Status */}

                      <td>

                        <span
                          className={`history-status ${
                            inspection.status === "PASS"
                              ? "history-pass"
                              : "history-defective"
                          }`}
                        >
                          {inspection.status}
                        </span>

                      </td>


                      {/* Defects */}

                      <td>

                        <strong>
                          {inspection.defect_count}
                        </strong>

                      </td>


                      {/* Severity */}

                      <td>

                        <span
                          className={`history-severity ${
                            inspection.severity
                              ?.toLowerCase() || ""
                          }`}
                        >
                          {formatSeverity(
                            inspection.severity
                          )}
                        </span>

                      </td>


                      {/* Risk */}

                      <td>

                        <span
                          className={`history-risk ${
                            inspection.risk
                              ?.toLowerCase() || ""
                          }`}
                        >
                          {inspection.risk || "-"}
                        </span>

                      </td>


                      {/* Decision */}

                      <td>

                        <span className="history-decision">

                          {formatDecision(
                            inspection.decision
                          )}

                        </span>

                      </td>


                      {/* Date */}

                      <td>

                        {new Date(
                          inspection.inspected_at
                        ).toLocaleString()}

                      </td>


                      {/* Action */}

                      <td>

                        <Link
                          to={`/inspections/${inspection.inspection_id}`}
                          className="view-button"
                        >
                          View
                        </Link>

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


export default History;