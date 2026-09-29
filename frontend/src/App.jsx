import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import NewInspection from "./pages/NewInspection";
import History from "./pages/History";
import InspectionDetails from "./pages/InspectionDetails";
import Register from "./pages/Register";

import "./App.css";


function App() {
  return (
    <BrowserRouter>

      <div className="app">

        <Routes>

          {/* ================================
              LOGIN
          ================================= */}

          <Route
            path="/login"
            element={<Login />}
          />
          <Route
              path="/register"
              element={<Register />}
          />


          {/* ================================
              PROTECTED APPLICATION
          ================================= */}

          <Route element={<ProtectedRoute />}>

            <Route
              path="/dashboard"
              element={
                <>
                  <Navbar />

                  <main className="container">
                    <Dashboard />
                  </main>
                </>
              }
            />


            <Route
              path="/inspection"
              element={
                <>
                  <Navbar />

                  <main className="container">
                    <NewInspection />
                  </main>
                </>
              }
            />


            <Route
              path="/history"
              element={
                <>
                  <Navbar />

                  <main className="container">
                    <History />
                  </main>
                </>
              }
            />


            <Route
              path="/inspections/:inspectionId"
              element={
                <>
                  <Navbar />

                  <main className="container">
                    <InspectionDetails />
                  </main>
                </>
              }
            />

          </Route>


          {/* ================================
              ROOT
          ================================= */}

          <Route
            path="/"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />


          {/* ================================
              UNKNOWN ROUTES
          ================================= */}

          <Route
            path="*"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

        </Routes>

      </div>

    </BrowserRouter>
  );
}


export default App;