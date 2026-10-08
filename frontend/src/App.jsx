import { useEffect, useState } from "react";
import "./index.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("access_token")
  );

  const [showRegister, setShowRegister] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [farmer, setFarmer] = useState(null);
  const [farms, setFarms] = useState([]);

  const [activePage, setActivePage] = useState("dashboard");

  const [message, setMessage] = useState("");
  const [chatMessages, setChatMessages] = useState([]);

  const [farmName, setFarmName] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");

  /* ============================================================
     CREATE SESSION ID
  ============================================================ */

  const getSessionId = () => {
    let sessionId = localStorage.getItem("agroagent_session_id");

    if (!sessionId) {
      sessionId =
        "session-" +
        Date.now() +
        "-" +
        Math.random().toString(36).substring(2, 10);

      localStorage.setItem(
        "agroagent_session_id",
        sessionId
      );
    }

    return sessionId;
  };

  /* ============================================================
     LOGIN
  ============================================================ */

  const handleLogin = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Login failed"
        );
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      localStorage.setItem(
        "farmer_id",
        data.farmer_id
      );

      localStorage.setItem(
        "farmer_name",
        data.name
      );

      localStorage.setItem(
        "farmer_email",
        data.email
      );

      /* Create a new chat session after login */

      const sessionId =
        "session-" +
        Date.now() +
        "-" +
        Math.random().toString(36).substring(2, 10);

      localStorage.setItem(
        "agroagent_session_id",
        sessionId
      );

      setFarmer({
        farmer_id: data.farmer_id,
        name: data.name,
        email: data.email,
      });

      setIsLoggedIn(true);

      setEmail("");
      setPassword("");

      setChatMessages([]);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /* ============================================================
     REGISTER
  ============================================================ */

  const handleRegister = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name,
            phone,
            email,
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Registration failed"
        );
      }

      alert(
        "Registration successful! Please login."
      );

      setShowRegister(false);

      setName("");
      setPhone("");
      setEmail("");
      setPassword("");

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  /* ============================================================
     LOGOUT
  ============================================================ */

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("farmer_id");
    localStorage.removeItem("farmer_name");
    localStorage.removeItem("farmer_email");
    localStorage.removeItem(
      "agroagent_session_id"
    );

    setIsLoggedIn(false);
    setFarmer(null);
    setFarms([]);
    setChatMessages([]);
    setActivePage("dashboard");
  };

  /* ============================================================
     LOAD FARMER
  ============================================================ */

  useEffect(() => {
    if (!isLoggedIn) return;

    const farmerId =
      localStorage.getItem("farmer_id");

    const farmerName =
      localStorage.getItem("farmer_name");

    const farmerEmail =
      localStorage.getItem("farmer_email");

    if (farmerId) {
      setFarmer({
        farmer_id: Number(farmerId),
        name: farmerName,
        email: farmerEmail,
      });

      loadFarms(Number(farmerId));
    }

    getSessionId();

  }, [isLoggedIn]);

  /* ============================================================
     LOAD FARMS
  ============================================================ */

  const loadFarms = async (farmerId) => {
    try {
      const token =
        localStorage.getItem("access_token");

      const response = await fetch(
        `${API_URL}/farmers/${farmerId}/farms`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (response.ok) {
        setFarms(
          data.farms ||
          data ||
          []
        );
      }

    } catch (err) {
      console.log(
        "Farm loading error:",
        err
      );
    }
  };

  /* ============================================================
     CREATE FARM
  ============================================================ */

  const handleCreateFarm = async (e) => {
    e.preventDefault();

    setError("");

    try {
      const token =
        localStorage.getItem("access_token");

      const farmerId =
        Number(
          localStorage.getItem("farmer_id")
        );

      const response = await fetch(
        `${API_URL}/farms`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify({
            farmer_id: farmerId,
            farm_name: farmName,
            latitude: Number(latitude),
            longitude: Number(longitude),
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Farm creation failed"
        );
      }

      alert(
        "Farm created successfully!"
      );

      setFarmName("");
      setLatitude("");
      setLongitude("");

      await loadFarms(farmerId);

    } catch (err) {
      setError(err.message);
    }
  };

  /* ============================================================
     FORMAT CHAT RESPONSE
  ============================================================ */

  const formatChatResponse = (value) => {
    if (
      value === null ||
      value === undefined
    ) {
      return "";
    }

    if (
      typeof value === "string"
    ) {
      return value;
    }

    if (
      typeof value === "number" ||
      typeof value === "boolean"
    ) {
      return String(value);
    }

    if (Array.isArray(value)) {
      return value
        .map((item) =>
          formatChatResponse(item)
        )
        .filter(Boolean)
        .join("\n");
    }

    if (
      typeof value === "object"
    ) {
      const preferredFields = [
        "response",
        "answer",
        "message",
        "final_answer",
        "final_response",
        "content",
        "result",
        "output",
        "text",
      ];

      for (
        const field of preferredFields
      ) {
        if (
          value[field] !== undefined &&
          value[field] !== null
        ) {
          const formatted =
            formatChatResponse(
              value[field]
            );

          if (formatted) {
            return formatted;
          }
        }
      }

      return JSON.stringify(
        value,
        null,
        2
      );
    }

    return String(value);
  };

  /* ============================================================
     CHAT
  ============================================================ */

  const handleChat = async (e) => {
    e.preventDefault();

    if (!message.trim()) {
      return;
    }

    const userMessage =
      message.trim();

    /* Add user message immediately */

    setChatMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: userMessage,
      },
    ]);

    setMessage("");

    try {
      const token =
        localStorage.getItem(
          "access_token"
        );

      const farmerId =
        Number(
          localStorage.getItem(
            "farmer_id"
          )
        );

      /* --------------------------------------------------------
         CHECK TOKEN
      -------------------------------------------------------- */

      if (!token) {
        throw new Error(
          "You are not logged in. Please login again."
        );
      }

      if (!farmerId) {
        throw new Error(
          "Farmer ID not found. Please login again."
        );
      }

      /* --------------------------------------------------------
         GET SESSION
      -------------------------------------------------------- */

      const sessionId =
        getSessionId();

      /* --------------------------------------------------------
         GET SELECTED FARM
         
         Backend automatically selects first farm if farm_id
         is not supplied.

         We send the first farm explicitly when available.
      -------------------------------------------------------- */

      let farmId = null;

      if (farms.length > 0) {
        farmId =
          farms[0].farm_id ??
          farms[0].id ??
          null;
      }

      /* --------------------------------------------------------
         CHAT REQUEST
      -------------------------------------------------------- */

      const requestBody = {
        session_id: sessionId,
        farmer_id: farmerId,
        farm_id: farmId,
        query: userMessage,
      };

      console.log(
        "AgroAgent Chat Request:",
        requestBody
      );

      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },

          body: JSON.stringify(
            requestBody
          ),
        }
      );

      /* --------------------------------------------------------
         RESPONSE
      -------------------------------------------------------- */

      const data =
        await response.json();

      console.log(
        "AgroAgent Chat Response:",
        data
      );

      if (!response.ok) {

        if (
          response.status === 401
        ) {
          localStorage.clear();

          setIsLoggedIn(false);

          throw new Error(
            "Session expired. Please login again."
          );
        }

        throw new Error(
          data.detail ||
          "Chat failed"
        );
      }

      /* --------------------------------------------------------
         GET ANSWER
      -------------------------------------------------------- */

      const rawAssistantResponse =
        data.answer ??
        data.response ??
        data.final_answer ??
        data.message ??
        data.output ??
        data.result ??
        data;

      const assistantText =
        formatChatResponse(
          rawAssistantResponse
        ) ||
        "I could not generate a response.";

      /* --------------------------------------------------------
         ADD AI RESPONSE
      -------------------------------------------------------- */

      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: assistantText,
        },
      ]);

    } catch (err) {

      console.error(
        "Chat error:",
        err
      );

      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text:
            `Error: ${err.message}`,
        },
      ]);
    }
  };

  /* ============================================================
     LOGIN / REGISTER SCREEN
  ============================================================ */

  if (!isLoggedIn) {
    return (
      <div className="auth-page">

        <div className="auth-left">

          <div className="brand-large">
            🌱 AgroAgent
          </div>

          <h1>
            Smart Farming
            <br />
            Powered by AI
          </h1>

          <p>
            Your autonomous agriculture assistant
            for crop recommendations, weather,
            soil, irrigation and plant disease analysis.
          </p>

          <div className="auth-features">

            <div>
              <span>🌾</span>

              <div>
                <strong>
                  Smart Crop Recommendations
                </strong>

                <small>
                  Choose crops using soil and weather data.
                </small>
              </div>
            </div>

            <div>
              <span>🌦️</span>

              <div>
                <strong>
                  Weather Intelligence
                </strong>

                <small>
                  Get weather information for your farm.
                </small>
              </div>
            </div>

            <div>
              <span>🤖</span>

              <div>
                <strong>
                  Autonomous AI Agent
                </strong>

                <small>
                  AI decides which agriculture tools to use.
                </small>
              </div>
            </div>

          </div>

        </div>

        <div className="auth-right">

          <div className="auth-card">

            {!showRegister ? (
              <>

                <div className="auth-heading">

                  <div className="auth-icon">
                    🌱
                  </div>

                  <h2>
                    Welcome Back
                  </h2>

                  <p>
                    Login to continue to your
                    AgroAgent dashboard.
                  </p>

                </div>

                <form
                  onSubmit={handleLogin}
                >

                  <label>
                    Email
                  </label>

                  <input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) =>
                      setEmail(e.target.value)
                    }
                    required
                  />

                  <label>
                    Password
                  </label>

                  <input
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) =>
                      setPassword(e.target.value)
                    }
                    required
                  />

                  {error && (
                    <div className="error-box">
                      {error}
                    </div>
                  )}

                  <button
                    className="primary-button"
                    type="submit"
                    disabled={loading}
                  >
                    {loading
                      ? "Logging in..."
                      : "Login"}
                  </button>

                </form>

                <div className="auth-switch">

                  Don't have an account?

                  <button
                    onClick={() => {
                      setShowRegister(true);
                      setError("");
                    }}
                  >
                    Create Account
                  </button>

                </div>

              </>
            ) : (

              <>

                <div className="auth-heading">

                  <div className="auth-icon">
                    🌾
                  </div>

                  <h2>
                    Create Account
                  </h2>

                  <p>
                    Create your farmer account
                    to use AgroAgent.
                  </p>

                </div>

                <form
                  onSubmit={handleRegister}
                >

                  <label>
                    Full Name
                  </label>

                  <input
                    type="text"
                    placeholder="Enter your name"
                    value={name}
                    onChange={(e) =>
                      setName(e.target.value)
                    }
                    required
                  />

                  <label>
                    Phone
                  </label>

                  <input
                    type="text"
                    placeholder="Enter phone number"
                    value={phone}
                    onChange={(e) =>
                      setPhone(e.target.value)
                    }
                  />

                  <label>
                    Email
                  </label>

                  <input
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) =>
                      setEmail(e.target.value)
                    }
                    required
                  />

                  <label>
                    Password
                  </label>

                  <input
                    type="password"
                    placeholder="Create a password"
                    value={password}
                    onChange={(e) =>
                      setPassword(e.target.value)
                    }
                    required
                  />

                  {error && (
                    <div className="error-box">
                      {error}
                    </div>
                  )}

                  <button
                    className="primary-button"
                    type="submit"
                    disabled={loading}
                  >
                    {loading
                      ? "Creating Account..."
                      : "Register"}
                  </button>

                </form>

                <div className="auth-switch">

                  Already have an account?

                  <button
                    onClick={() => {
                      setShowRegister(false);
                      setError("");
                    }}
                  >
                    Login
                  </button>

                </div>

              </>
            )}

          </div>

        </div>

      </div>
    );
  }

  /* ============================================================
     DASHBOARD
  ============================================================ */

  return (
    <div className="app-layout">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="sidebar-logo">

          <div className="logo-symbol">
            🌱
          </div>

          <div>
            <h2>
              AgroAgent
            </h2>

            <span>
              AI Agriculture
            </span>
          </div>

        </div>

        <div className="sidebar-menu">

          <button
            className={
              activePage === "dashboard"
                ? "menu-item active"
                : "menu-item"
            }
            onClick={() =>
              setActivePage("dashboard")
            }
          >
            <span>🏠</span>
            Dashboard
          </button>

          <button
            className={
              activePage === "farms"
                ? "menu-item active"
                : "menu-item"
            }
            onClick={() =>
              setActivePage("farms")
            }
          >
            <span>🌾</span>
            My Farms
          </button>

          <button
            className={
              activePage === "chat"
                ? "menu-item active"
                : "menu-item"
            }
            onClick={() =>
              setActivePage("chat")
            }
          >
            <span>🤖</span>
            Ask AgroAgent
          </button>

          <button
            className={
              activePage === "weather"
                ? "menu-item active"
                : "menu-item"
            }
            onClick={() =>
              setActivePage("weather")
            }
          >
            <span>🌦️</span>
            Weather
          </button>

          <button
            className={
              activePage === "soil"
                ? "menu-item active"
                : "menu-item"
            }
            onClick={() =>
              setActivePage("soil")
            }
          >
            <span>🌱</span>
            Soil Analysis
          </button>

          <button
            className={
              activePage === "disease"
                ? "menu-item active"
                : "menu-item"
            }
            onClick={() =>
              setActivePage("disease")
            }
          >
            <span>🔬</span>
            Disease Detection
          </button>

        </div>

        <div className="sidebar-bottom">

          <div className="user-mini">

            <div className="avatar">
              {farmer?.name
                ?.charAt(0)
                ?.toUpperCase() || "F"}
            </div>

            <div>

              <strong>
                {farmer?.name || "Farmer"}
              </strong>

              <small>
                {farmer?.email || ""}
              </small>

            </div>

          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
          >
            🚪 Logout
          </button>

        </div>

      </aside>

      {/* MAIN CONTENT */}

      <main className="main-content">

        {/* HEADER */}

        <header className="topbar">

          <div>

            <h1>
              {activePage === "dashboard" &&
                "Dashboard"}

              {activePage === "farms" &&
                "My Farms"}

              {activePage === "chat" &&
                "Ask AgroAgent"}

              {activePage === "weather" &&
                "Weather"}

              {activePage === "soil" &&
                "Soil Analysis"}

              {activePage === "disease" &&
                "Disease Detection"}
            </h1>

            <p>
              Welcome back,{" "}
              {farmer?.name || "Farmer"} 👋
            </p>

          </div>

          <div className="topbar-user">

            <div className="avatar">
              {farmer?.name
                ?.charAt(0)
                ?.toUpperCase() || "F"}
            </div>

            <div>

              <strong>
                {farmer?.name || "Farmer"}
              </strong>

              <small>
                Farmer
              </small>

            </div>

          </div>

        </header>

        {/* ERROR */}

        {error &&
          activePage !== "dashboard" && (
            <div className="error-box main-error">
              {error}
            </div>
          )}

        {/* ======================================================
           DASHBOARD
        ====================================================== */}

        {activePage === "dashboard" && (

          <div className="dashboard">

            <section className="hero-card">

              <div className="hero-text">

                <span className="hero-label">
                  🤖 AUTONOMOUS AGRICULTURE AI
                </span>

                <h2>
                  Your Farm.
                  <br />
                  <span>
                    Your AI Assistant.
                  </span>
                </h2>

                <p>
                  Ask AgroAgent anything about
                  your crops, soil, weather,
                  irrigation or plant diseases.
                  The AI agent decides which
                  tools to use.
                </p>

                <button
                  className="hero-button"
                  onClick={() =>
                    setActivePage("chat")
                  }
                >
                  Ask AgroAgent →
                </button>

              </div>

              <div className="hero-visual">

                <div className="sun">
                  ☀️
                </div>

                <div className="farm-illustration">
                  🌾 🌾 🌾
                </div>

                <div className="robot">
                  🤖
                </div>

              </div>

            </section>

            {/* STATS */}

            <section className="stats-grid">

              <div className="stat-card">

                <div className="stat-icon">
                  🌾
                </div>

                <div>

                  <span>
                    My Farms
                  </span>

                  <strong>
                    {farms.length}
                  </strong>

                </div>

              </div>

              <div className="stat-card">

                <div className="stat-icon">
                  🤖
                </div>

                <div>

                  <span>
                    AI Assistant
                  </span>

                  <strong>
                    Active
                  </strong>

                </div>

              </div>

              <div className="stat-card">

                <div className="stat-icon">
                  🌦️
                </div>

                <div>

                  <span>
                    Weather
                  </span>

                  <strong>
                    Available
                  </strong>

                </div>

              </div>

              <div className="stat-card">

                <div className="stat-icon">
                  🔬
                </div>

                <div>

                  <span>
                    Disease AI
                  </span>

                  <strong>
                    Ready
                  </strong>

                </div>

              </div>

            </section>

            {/* QUICK ACTIONS */}

            <section className="section">

              <div className="section-heading">

                <div>

                  <h2>
                    Quick Actions
                  </h2>

                  <p>
                    Access your agriculture
                    AI tools quickly.
                  </p>

                </div>

              </div>

              <div className="quick-grid">

                <button
                  onClick={() =>
                    setActivePage("chat")
                  }
                  className="quick-card"
                >

                  <div className="quick-icon">
                    🤖
                  </div>

                  <h3>
                    Ask AgroAgent
                  </h3>

                  <p>
                    Get AI-powered agriculture
                    recommendations.
                  </p>

                  <span>
                    Open Assistant →
                  </span>

                </button>

                <button
                  onClick={() =>
                    setActivePage("farms")
                  }
                  className="quick-card"
                >

                  <div className="quick-icon">
                    🌾
                  </div>

                  <h3>
                    Manage Farms
                  </h3>

                  <p>
                    Add and manage your
                    farm information.
                  </p>

                  <span>
                    View Farms →
                  </span>

                </button>

                <button
                  onClick={() =>
                    setActivePage("weather")
                  }
                  className="quick-card"
                >

                  <div className="quick-icon">
                    🌦️
                  </div>

                  <h3>
                    Weather
                  </h3>

                  <p>
                    Check weather conditions
                    for your farm.
                  </p>

                  <span>
                    Check Weather →
                  </span>

                </button>

                <button
                  onClick={() =>
                    setActivePage("disease")
                  }
                  className="quick-card"
                >

                  <div className="quick-icon">
                    🔬
                  </div>

                  <h3>
                    Disease Detection
                  </h3>

                  <p>
                    Analyze plant images
                    using AI.
                  </p>

                  <span>
                    Analyze Plant →
                  </span>

                </button>

              </div>

            </section>

            {/* AGENT FLOW */}

            <section className="agent-section">

              <div className="section-heading">

                <div>

                  <h2>
                    How AgroAgent Works
                  </h2>

                  <p>
                    An autonomous AI workflow
                    for agriculture.
                  </p>

                </div>

              </div>

              <div className="agent-flow">

                <div className="flow-step">

                  <div>
                    💬
                  </div>

                  <strong>
                    Ask
                  </strong>

                  <span>
                    Farmer asks a question
                  </span>

                </div>

                <div className="flow-arrow">
                  →
                </div>

                <div className="flow-step">

                  <div>
                    🧠
                  </div>

                  <strong>
                    Plan
                  </strong>

                  <span>
                    AI selects tools
                  </span>

                </div>

                <div className="flow-arrow">
                  →
                </div>

                <div className="flow-step">

                  <div>
                    ⚙️
                  </div>

                  <strong>
                    Execute
                  </strong>

                  <span>
                    Tools perform tasks
                  </span>

                </div>

                <div className="flow-arrow">
                  →
                </div>

                <div className="flow-step">

                  <div>
                    ✅
                  </div>

                  <strong>
                    Verify
                  </strong>

                  <span>
                    AI checks the result
                  </span>

                </div>

                <div className="flow-arrow">
                  →
                </div>

                <div className="flow-step">

                  <div>
                    💡
                  </div>

                  <strong>
                    Respond
                  </strong>

                  <span>
                    Farmer gets answer
                  </span>

                </div>

              </div>

            </section>

          </div>
        )}

        {/* ======================================================
           FARMS
        ====================================================== */}

        {activePage === "farms" && (

          <div className="page-container">

            <div className="page-intro">

              <h2>
                My Farms
              </h2>

              <p>
                Manage the farms connected
                to your AgroAgent account.
              </p>

            </div>

            <div className="farm-layout">

              <div className="panel">

                <h3>
                  Add New Farm
                </h3>

                <form
                  onSubmit={handleCreateFarm}
                >

                  <label>
                    Farm Name
                  </label>

                  <input
                    type="text"
                    placeholder="Example: My Farm"
                    value={farmName}
                    onChange={(e) =>
                      setFarmName(
                        e.target.value
                      )
                    }
                    required
                  />

                  <label>
                    Latitude
                  </label>

                  <input
                    type="number"
                    step="any"
                    placeholder="17.3850"
                    value={latitude}
                    onChange={(e) =>
                      setLatitude(
                        e.target.value
                      )
                    }
                    required
                  />

                  <label>
                    Longitude
                  </label>

                  <input
                    type="number"
                    step="any"
                    placeholder="78.4867"
                    value={longitude}
                    onChange={(e) =>
                      setLongitude(
                        e.target.value
                      )
                    }
                    required
                  />

                  <button
                    className="primary-button"
                    type="submit"
                  >
                    + Add Farm
                  </button>

                </form>

              </div>

              <div className="panel">

                <h3>
                  Your Farms
                </h3>

                {farms.length === 0 ? (

                  <div className="empty-state">

                    <div>
                      🌾
                    </div>

                    <h4>
                      No farms added yet
                    </h4>

                    <p>
                      Add your first farm
                      to start using
                      agriculture intelligence.
                    </p>

                  </div>

                ) : (

                  <div className="farm-list">

                    {farms.map(
                      (farm, index) => (

                        <div
                          className="farm-item"
                          key={
                            farm.farm_id ||
                            farm.id ||
                            index
                          }
                        >

                          <div className="farm-item-icon">
                            🌾
                          </div>

                          <div>

                            <h4>
                              {farm.farm_name ||
                                farm.name ||
                                "Farm"}
                            </h4>

                            <p>
                              📍{" "}
                              {farm.latitude ??
                                "N/A"}
                              ,{" "}
                              {farm.longitude ??
                                "N/A"}
                            </p>

                          </div>

                        </div>

                      )
                    )}

                  </div>

                )}

              </div>

            </div>

          </div>
        )}

        {/* ======================================================
           CHAT
        ====================================================== */}

        {activePage === "chat" && (

          <div className="chat-page">

            <div className="chat-header-card">

              <div className="agent-avatar">
                🤖
              </div>

              <div>

                <h2>
                  AgroAgent AI
                </h2>

                <p>
                  Autonomous agriculture assistant
                  <span className="online-dot"></span>
                </p>

              </div>

            </div>

            <div className="chat-window">

              {chatMessages.length === 0 && (

                <div className="chat-welcome">

                  <div className="big-robot">
                    🤖
                  </div>

                  <h2>
                    How can I help with your farm?
                  </h2>

                  <p>
                    Ask me about crops, weather,
                    soil, irrigation or plant diseases.
                  </p>

                  <div className="suggestion-grid">

                    <button
                      onClick={() =>
                        setMessage(
                          "Which crop should I grow?"
                        )
                      }
                    >
                      🌾 Which crop should I grow?
                    </button>

                    <button
                      onClick={() =>
                        setMessage(
                          "What is the weather forecast?"
                        )
                      }
                    >
                      🌦️ What is the weather forecast?
                    </button>

                    <button
                      onClick={() =>
                        setMessage(
                          "Should I irrigate my crop?"
                        )
                      }
                    >
                      💧 Should I irrigate my crop?
                    </button>

                    <button
                      onClick={() =>
                        setMessage(
                          "How can I detect plant disease?"
                        )
                      }
                    >
                      🔬 Detect plant disease
                    </button>

                  </div>

                </div>

              )}

              {chatMessages.map(
                (chat, index) => (

                  <div
                    key={index}
                    className={
                      chat.role === "user"
                        ? "chat-message user-message"
                        : "chat-message assistant-message"
                    }
                  >

                    <div className="message-avatar">

                      {chat.role === "user"
                        ? "👨‍🌾"
                        : "🤖"}

                    </div>

                    <div className="message-bubble">

                      {typeof chat.text ===
                      "string"
                        ? chat.text
                        : JSON.stringify(
                            chat.text,
                            null,
                            2
                          )}

                    </div>

                  </div>

                )
              )}

            </div>

            <form
              className="chat-input-area"
              onSubmit={handleChat}
            >

              <input
                type="text"
                placeholder="Ask AgroAgent about your farm..."
                value={message}
                onChange={(e) =>
                  setMessage(
                    e.target.value
                  )
                }
              />

              <button
                type="submit"
              >
                ➤
              </button>

            </form>

          </div>
        )}

        {/* ======================================================
           WEATHER
        ====================================================== */}

        {activePage === "weather" && (

          <div className="page-container">

            <div className="feature-placeholder">

              <div className="feature-large-icon">
                🌦️
              </div>

              <h2>
                Weather Intelligence
              </h2>

              <p>
                AgroAgent can use weather data
                to provide current conditions
                and forecasts for your farm.
              </p>

              <button
                className="primary-button"
                onClick={() =>
                  setActivePage("chat")
                }
              >
                Ask AgroAgent About Weather
              </button>

            </div>

          </div>
        )}

        {/* ======================================================
           SOIL
        ====================================================== */}

        {activePage === "soil" && (

          <div className="page-container">

            <div className="feature-placeholder">

              <div className="feature-large-icon">
                🌱
              </div>

              <h2>
                Soil Analysis
              </h2>

              <p>
                Analyze soil properties and
                get crop suitability
                recommendations using AgroAgent.
              </p>

              <button
                className="primary-button"
                onClick={() =>
                  setActivePage("chat")
                }
              >
                Ask About Soil
              </button>

            </div>

          </div>
        )}

        {/* ======================================================
           DISEASE
        ====================================================== */}

        {activePage === "disease" && (

          <div className="page-container">

            <div className="feature-placeholder">

              <div className="feature-large-icon">
                🔬
              </div>

              <h2>
                Plant Disease Detection
              </h2>

              <p>
                Upload a plant image through
                the disease detection API to
                analyze possible diseases.
              </p>

              <button
                className="primary-button"
                onClick={() =>
                  setActivePage("chat")
                }
              >
                Ask AgroAgent
              </button>

            </div>

          </div>
        )}

      </main>

    </div>
  );
}

export default App;