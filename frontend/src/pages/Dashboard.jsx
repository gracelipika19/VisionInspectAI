import { useEffect, useState } from "react";
import api from "../services/api";


function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  // -------------------------------------------------------
  // Fetch dashboard statistics
  // -------------------------------------------------------

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get("/stats");

        setStats(response.data);
      } catch (err) {
        console.error(err);

        setError(
          "Unable to load dashboard statistics."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);


  // -------------------------------------------------------
  // Loading state
  // -------------------------------------------------------

  if (loading) {
    return (
      <section className="dashboard-page">
        <div className="dashboard-message">
          Loading dashboard...
        </div>
      </section>
    );
  }


  // -------------------------------------------------------
  // Error state
  // -------------------------------------------------------

  if (error) {
    return (
      <section className="dashboard-page">
        <div className="dashboard-error">
          {error}
        </div>
      </section>
    );
  }


  // -------------------------------------------------------
  // Dashboard
  // -------------------------------------------------------

  return (
    <section className="dashboard-page">

      <div className="dashboard-header">

        <div>
          <h2>
            Dashboard
          </h2>

          <p>
            PCB quality inspection overview
          </p>
        </div>

      </div>


      {/* -------------------------------------------------
          Statistics Cards
      -------------------------------------------------- */}

      <div className="dashboard-stats">

        <div className="dashboard-stat-card">

          <span>
            Total Inspections
          </span>

          <strong>
            {stats.total_inspections}
          </strong>

        </div>


        <div className="dashboard-stat-card">

          <span>
            Defective Boards
          </span>

          <strong>
            {stats.defective_inspections}
          </strong>

        </div>


        <div className="dashboard-stat-card">

          <span>
            Passed Boards
          </span>

          <strong>
            {stats.passed_inspections}
          </strong>

        </div>


        <div className="dashboard-stat-card">

          <span>
            Total Defects
          </span>

          <strong>
            {stats.total_defects}
          </strong>

        </div>

      </div>


      {/* -------------------------------------------------
          Defect Distribution
      -------------------------------------------------- */}

      <div className="distribution-card">

        <div className="distribution-header">

          <h3>
            Defect Distribution
          </h3>

          <span>
            Detected defect count
          </span>

        </div>


        {Object.keys(stats.defect_distribution).length === 0 ? (

          <p className="no-defects">
            No defects have been detected yet.
          </p>

        ) : (

          <div className="distribution-list">

            {Object.entries(
              stats.defect_distribution
            ).map(([className, count]) => (

              <div
                className="distribution-row"
                key={className}
              >

                <div className="distribution-name">

                  <span>
                    {className.replaceAll(
                      "_",
                      " "
                    )}
                  </span>

                  <strong>
                    {count}
                  </strong>

                </div>


                <div className="distribution-bar">

                  <div
                    className="distribution-fill"
                    style={{
                      width: `${
                        stats.total_defects > 0
                          ? (count /
                              stats.total_defects) *
                            100
                          : 0
                      }%`,
                    }}
                  />

                </div>

              </div>

            ))}

          </div>

        )}

      </div>

    </section>
  );
}


export default Dashboard;