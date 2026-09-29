import { NavLink } from "react-router-dom";
import { logoutUser } from "../services/api";


function Navbar() {

  const handleLogout = () => {
    logoutUser();
  };


  return (
    <header className="navbar">

      <div className="navbar-inner">

        {/* ==================================================
            Brand
        ================================================== */}

        <NavLink
          to="/"
          className="navbar-brand"
        >

          <div className="navbar-title">
            VisionInspect AI
          </div>

          <div className="navbar-subtitle">
            PCB Quality Inspection
          </div>

        </NavLink>


        {/* ==================================================
            Navigation
        ================================================== */}

        <nav className="navbar-links">

          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive
                ? "nav-link active"
                : "nav-link"
            }
          >
            Dashboard
          </NavLink>


          <NavLink
            to="/inspection"
            className={({ isActive }) =>
              isActive
                ? "nav-link active"
                : "nav-link"
            }
          >
            New Inspection
          </NavLink>


          <NavLink
            to="/history"
            className={({ isActive }) =>
              isActive
                ? "nav-link active"
                : "nav-link"
            }
          >
            History
          </NavLink>


          <button
            type="button"
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>

        </nav>

      </div>

    </header>
  );
}


export default Navbar;