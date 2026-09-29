import { useState } from "react";
import {
  Link,
  useNavigate,
} from "react-router-dom";

import {
  loginUser,
  getCurrentUser,
} from "../services/api";


function Login() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  // ==================================================
  // Handle Login
  // ==================================================

  const handleLogin = async (event) => {
    event.preventDefault();

    if (!username.trim() || !password) {
      setError(
        "Please enter your username and password."
      );
      return;
    }

    try {
      setLoading(true);
      setError("");

      // ----------------------------------------------
      // Step 1: Login and receive JWT
      // ----------------------------------------------

      const loginData = await loginUser(
        username.trim(),
        password
      );

      localStorage.setItem(
        "access_token",
        loginData.access_token
      );


      // ----------------------------------------------
      // Step 2: Get authenticated user
      // ----------------------------------------------

      const user = await getCurrentUser();

      localStorage.setItem(
        "user",
        JSON.stringify(user)
      );


      // ----------------------------------------------
      // Step 3: Go to dashboard
      // ----------------------------------------------

      navigate("/dashboard");

    } catch (err) {
      console.error("Login error:", err);

      // Remove invalid authentication data
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");

      setError(
        err.response?.data?.detail ||
        "Login failed. Please check your credentials."
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="login-page">

      <div className="login-card">

        {/* ==================================================
            Brand
        ================================================== */}

        <div className="login-brand">

          <div className="login-logo">
            VI
          </div>

          <div>

            <h1>
              VisionInspect AI
            </h1>

            <p>
              PCB Quality Inspection System
            </p>

          </div>

        </div>


        {/* ==================================================
            Welcome Message
        ================================================== */}

        <div className="login-heading">

          <h2>
            Welcome back
          </h2>

          <p>
            Sign in to access the inspection platform.
          </p>

        </div>


        {/* ==================================================
            Login Form
        ================================================== */}

        <form
          className="login-form"
          onSubmit={handleLogin}
        >

          {/* Username */}

          <div className="form-group">

            <label htmlFor="username">
              Username
            </label>

            <input
              id="username"
              type="text"
              value={username}
              onChange={(event) =>
                setUsername(event.target.value)
              }
              placeholder="Enter your username"
              autoComplete="username"
              disabled={loading}
            />

          </div>


          {/* Password */}

          <div className="form-group">

            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Enter your password"
              autoComplete="current-password"
              disabled={loading}
            />

          </div>


          {/* Error Message */}

          {error && (

            <div className="login-error">
              {error}
            </div>

          )}


          {/* Login Button */}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >

            {loading
              ? "Signing in..."
              : "Sign In"}

          </button>

        </form>


        {/* ==================================================
            Register Link
        ================================================== */}

        <div className="register-login-link">

          Don't have an account?{" "}

          <Link to="/register">
            Create an account
          </Link>

        </div>


        {/* ==================================================
            Platform Roles
        ================================================== */}

        <div className="role-info">

          <p className="role-info-title">
            Platform Access
          </p>


          <div className="role-list">

            {/* Quality Engineer */}

            <div className="role-item">

              <span className="role-icon">
                ⚙
              </span>

              <div>

                <strong>
                  Quality Engineer
                </strong>

                <span>
                  AI inspection & quality analysis
                </span>

              </div>

            </div>


            {/* Supervisor */}

            <div className="role-item">

              <span className="role-icon">
                📊
              </span>

              <div>

                <strong>
                  Supervisor
                </strong>

                <span>
                  Production & quality analytics
                </span>

              </div>

            </div>

          </div>

        </div>


        {/* ==================================================
            Footer
        ================================================== */}

        <p className="login-footer">
          VisionInspect AI • Manufacturing Quality Platform
        </p>

      </div>

    </div>
  );
}


export default Login;