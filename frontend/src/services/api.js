import axios from "axios";


const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


const api = axios.create({
  baseURL: API_BASE_URL,
});


// ==================================================
// Request Interceptor
// Attach JWT to protected API requests
// ==================================================

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },

  (error) => {
    return Promise.reject(error);
  }
);


// ==================================================
// Response Interceptor
// Handle expired / invalid JWT
// ==================================================

api.interceptors.response.use(
  (response) => {
    return response;
  },

  (error) => {
    if (error.response?.status === 401) {

      localStorage.removeItem("access_token");
      localStorage.removeItem("user");

      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  }
);


// ==================================================
// Login
// ==================================================

export const loginUser = async (
  username,
  password
) => {

  const formData = new URLSearchParams();

  formData.append("username", username);
  formData.append("password", password);


  const response = await api.post(
    "/auth/login",
    formData,
    {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    }
  );


  return response.data;
};


// ==================================================
// Get Current User
// ==================================================

export const getCurrentUser = async () => {

  const response = await api.get(
    "/auth/me"
  );

  return response.data;
};


// ==================================================
// Inspect PCB Image
// ==================================================

export const inspectImage = async (file) => {

  const formData = new FormData();

  formData.append("file", file);


  const response = await api.post(
    "/predict",
    formData,
    {
      headers: {
        "Content-Type":
          "multipart/form-data",
      },
    }
  );


  return response.data;
};


// ==================================================
// Logout
// ==================================================

export const logoutUser = () => {

  localStorage.removeItem("access_token");
  localStorage.removeItem("user");

  window.location.href = "/login";
};


export default api;

// ==================================================
// Register User
// ==================================================

export const registerUser = async (
  username,
  email,
  password
) => {
  const formData = new URLSearchParams();

  formData.append("username", username);
  formData.append("email", email);
  formData.append("password", password);

  // Normal registration creates a Quality Engineer.
  formData.append(
    "role",
    "QUALITY_ENGINEER"
  );

  const response = await api.post(
    "/auth/register",
    formData,
    {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    }
  );

  return response.data;
};