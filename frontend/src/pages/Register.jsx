import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { registerUser } from "../services/api";


function Register() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");


  const handleRegister = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (
      !username.trim() ||
      !email.trim() ||
      !password ||
      !confirmPassword
    ) {
      setError("Please fill in all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    try {
      setLoading(true);

      await registerUser(
        username.trim(),
        email.trim(),
        password
      );

      setSuccess(
        "Account created successfully. Redirecting to login..."
      );

      setTimeout(() => {
        navigate("/login");
      }, 1200);

    } catch (err) {
      console.error("Registration error:", err);

      setError(
        err.response?.data?.detail ||
        "Registration failed. Please try again."
      );

    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="login-page">

      <div className="login-card">

        {/* Brand */}

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


        {/* Heading */}

        <div className="login-heading">

          <h2>
            Create your account
          </h2>

          <p>
            Register to access the inspection platform.
          </p>

        </div>


        {/* Registration Form */}

        <form
          className="login-form"
          onSubmit={handleRegister}
        >

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


          <div className="form-group">

            <label htmlFor="email">
              Email
            </label>

            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="Enter your email"
              autoComplete="email"
              disabled={loading}
            />

          </div>


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
              placeholder="Create a password"
              autoComplete="new-password"
              disabled={loading}
            />

          </div>


          <div className="form-group">

            <label htmlFor="confirmPassword">
              Confirm Password
            </label>

            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(event) =>
                setConfirmPassword(event.target.value)
              }
              placeholder="Confirm your password"
              autoComplete="new-password"
              disabled={loading}
            />

          </div>


          {/* Default role */}

          <div className="register-role">

            <span>
              Account Role
            </span>

            <strong>
              Quality Engineer
            </strong>

            <small>
              New accounts are created with Quality
              Engineer access.
            </small>

          </div>


          {error && (
            <div className="login-error">
              {error}
            </div>
          )}


          {success && (
            <div className="login-success">
              {success}
            </div>
          )}


          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading
              ? "Creating account..."
              : "Create Account"}
          </button>

        </form>


        {/* Login Link */}

        <div className="register-login-link">

          Already have an account?{" "}

          <Link to="/login">
            Sign in
          </Link>

        </div>


        <p className="login-footer">
          VisionInspect AI • Manufacturing Quality Platform
        </p>

      </div>

    </div>
  );
}


export default Register;