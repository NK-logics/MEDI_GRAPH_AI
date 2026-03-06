import React, { useMemo, useState, useEffect } from "react";
import GraphPanel from "./GraphPanel";

const TOKEN_KEY = "memory_graph_token";

function App() {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [userId, setUserId] = useState(() => localStorage.getItem("user_id") || "");
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || "");

  const isAuthenticated = Boolean(token);

  const title = useMemo(() => {
    return mode === "login" ? "Welcome Back" : "Create Your Graph Space";
  }, [mode]);

  // Add animation styles
  useEffect(() => {
    // Ensure body has dark background
    document.body.style.backgroundColor = "#0d1117";
    document.body.style.margin = "0";
    document.body.style.padding = "0";
    
    const styleSheet = document.createElement("style");
    styleSheet.textContent = `
      @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
      }
      @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      * {
        box-sizing: border-box;
      }
      html, body {
        background-color: #0d1117 !important;
        margin: 0;
        padding: 0;
        min-height: 100vh;
      }
      #root {
        background-color: #0d1117;
        min-height: 100vh;
      }
    `;
    document.head.appendChild(styleSheet);
    return () => styleSheet.remove();
  }, []);

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (mode === "signup") {
        const signupRes = await fetch("/signup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name, email, password }),
        });
        const signupData = await signupRes.json();
        if (!signupRes.ok || signupData.error) {
          throw new Error(signupData.error || "Signup failed");
        }
      }

      const loginRes = await fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const loginData = await loginRes.json();
      if (!loginRes.ok || loginData.error || !loginData.access_token) {
        throw new Error(loginData.error || "Login failed");
      }

      localStorage.setItem(TOKEN_KEY, loginData.access_token);
      localStorage.setItem("user_id", loginData.user_id);
      setToken(loginData.access_token);
      setUserId(loginData.user_id);
    } catch (err) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem("user_id");
    setToken("");
    setUserId("");
  }

  if (isAuthenticated) {
    return (
      <div style={styles.appShell}>
        <header style={styles.topBar}>
          <div style={styles.logo}>
            <div style={styles.logoMark}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0d1117" strokeWidth="2.5">
                <circle cx="5" cy="12" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="19" cy="19" r="2"/>
                <line x1="7" y1="12" x2="17" y2="6"/><line x1="7" y1="12" x2="17" y2="18"/>
              </svg>
            </div>
            MediGraph
          </div>
          <nav style={styles.nav}>
            <a href="#graph" style={styles.navLink}>Visualization</a>
            <a href="#features" style={styles.navLink}>Features</a>
            <a href="#stack" style={styles.navLink}>Stack</a>
            <a href="#demo" style={styles.navLink}>Demo</a>
          </nav>
          <div style={styles.userSection}>
            <span style={styles.userEmail}>{userId || "user"}</span>
            <button type="button" onClick={handleLogout} style={styles.logoutButton}>
              Logout
            </button>
          </div>
        </header>
        <main style={styles.graphWrap}>
          <GraphPanel token={token} onUnauthorized={handleLogout} />
        </main>
      </div>
    );
  }

  return (
    <div style={styles.authScene}>
      {/* Dark base layer */}
      <div style={styles.darkBase} />
      
      {/* Background elements */}
      <div style={styles.backgroundGradient} />
      <div style={styles.gridPattern} />
      
      {/* Hero section with split layout */}
      <div style={styles.splitContainer}>
        {/* Left side - Hero content */}
        <div style={styles.heroSection}>
          <div style={styles.heroContent}>

            <h1 style={styles.heroTitle}>
              Explore Personal Health
              <br />
              <span style={styles.heroHighlight}>as a Living Graph</span>
            </h1>
            <p style={styles.heroDescription}>
              A privacy-aware healthcare memory assistant that stores
              symptoms, medications, triggers, and lifestyle history
              as a dynamic knowledge graph for explainable insights
              and smarter doctor consultations.
            </p>
            <div style={styles.heroButtons}>
              <button style={styles.primaryButton}>See Visualization →</button>
              <button style={styles.secondaryButton}>Chat+Graph Demo</button>
            </div>
           
          </div>
        </div>

        {/* Right side - Auth card */}
        <div style={styles.authSection}>
          <section style={styles.authCard}>
            <h2 style={styles.title}>{title}</h2>
            <p style={styles.subtitle}>
              Authenticate to access your personal health graph
            </p>

            <div style={styles.toggleWrap}>
              <button
                type="button"
                onClick={() => setMode("login")}
                style={mode === "login" ? styles.toggleActive : styles.toggle}
              >
                Login
              </button>
              <button
                type="button"
                onClick={() => setMode("signup")}
                style={mode === "signup" ? styles.toggleActive : styles.toggle}
              >
                Sign Up
              </button>
            </div>

            <form onSubmit={handleAuthSubmit} style={styles.form}>
              {mode === "signup" ? (
                <input
                  style={styles.input}
                  type="text"
                  placeholder="Full name"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  required
                />
              ) : null}
              <input
                style={styles.input}
                type="email"
                placeholder="Email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
              <input
                style={styles.input}
                type="password"
                placeholder="Password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />

              {error ? <div style={styles.error}>{error}</div> : null}

              <button type="submit" style={styles.submitButton} disabled={loading}>
                {loading ? "Authenticating..." : mode === "login" ? "Login →" : "Sign Up →"}
              </button>
            </form>
          </section>
        </div>
      </div>
    </div>
  );
}

const styles = {
  appShell: {
    minHeight: "100vh",
    background: "#0d1117",
    color: "#dde5f4",
    fontFamily: "'DM Mono', 'Inter', monospace",
  },
  topBar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0 48px",
    height: "60px",
    background: "rgba(13,17,23,0.95)",
    backdropFilter: "blur(14px)",
    borderBottom: "1px solid #252f42",
  },
  logo: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    fontFamily: "'Clash Display', sans-serif",
    fontSize: "20px",
    fontWeight: 700,
    letterSpacing: "-0.5px",
    color: "#dde5f4",
  },
  logoMark: {
    width: "30px",
    height: "30px",
    background: "#4ecdc4",
    borderRadius: "7px",
    display: "grid",
    placeItems: "center",
  },
  nav: {
    display: "flex",
    gap: "32px",
    listStyle: "none",
  },
  navLink: {
    color: "#5c7099",
    textDecoration: "none",
    fontSize: "12px",
    letterSpacing: "0.5px",
    transition: "color 0.2s",
    ":hover": {
      color: "#4ecdc4",
    },
  },
  userSection: {
    display: "flex",
    alignItems: "center",
    gap: "16px",
  },
  userEmail: {
    color: "#5c7099",
    fontSize: "12px",
  },
  logoutButton: {
    padding: "8px 20px",
    background: "#4ecdc4",
    color: "#0d1117",
    border: "none",
    borderRadius: "8px",
    fontFamily: "'Clash Display', sans-serif",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
    transition: "opacity 0.2s",
    ":hover": {
      opacity: 0.85,
    },
  },
  graphWrap: {
    height: "calc(100vh - 60px)",
    padding: "20px",
    background: "#0d1117",
  },
  authScene: {
    minHeight: "100vh",
    position: "relative",
    overflow: "hidden",
    fontFamily: "'DM Mono', monospace",
    background: "#0d1117",
    backgroundColor: "#0d1117",
  },
  darkBase: {
    position: "absolute",
    inset: 0,
    background: "#0d1117",
    zIndex: 0,
  },
  backgroundGradient: {
    position: "absolute",
    inset: 0,
    background: "radial-gradient(ellipse 70% 55% at 50% 50%, rgba(78,205,196,0.08) 0%, transparent 70%)",
    zIndex: 1,
  },
  gridPattern: {
    position: "absolute",
    inset: 0,
    backgroundImage: `
      linear-gradient(#252f42 1px, transparent 1px),
      linear-gradient(90deg, #252f42 1px, transparent 1px)
    `,
    backgroundSize: "60px 60px",
    opacity: 0.35,
    zIndex: 2,
  },
  splitContainer: {
    position: "relative",
    zIndex: 3,
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    minHeight: "100vh",
    background: "transparent",
  },
  heroSection: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "40px",
    color: "#dde5f4",
    background: "transparent",
  },
  heroContent: {
    maxWidth: "560px",
    animation: "fadeUp 0.8s ease",
  },
  heroBadge: {
    display: "inline-flex",
    alignItems: "center",
    gap: "7px",
    padding: "5px 14px",
    background: "rgba(78,205,196,0.08)",
    border: "1px solid rgba(78,205,196,0.25)",
    borderRadius: "20px",
    fontSize: "11px",
    color: "#4ecdc4",
    letterSpacing: "1px",
    textTransform: "uppercase",
    marginBottom: "28px",
  },
  badgeDot: {
    width: "6px",
    height: "6px",
    borderRadius: "50%",
    background: "#4ecdc4",
    boxShadow: "0 0 8px #4ecdc4",
    animation: "blink 2s ease-in-out infinite",
  },
  heroTitle: {
    fontFamily: "'Clash Display', sans-serif",
    fontSize: "clamp(42px, 10vw, 58px)",
    fontWeight: 700,
    lineHeight: 1.0,
    letterSpacing: "-2px",
    marginBottom: "24px",
  },
  heroHighlight: {
    color: "#4ecdc4",
  },
  heroDescription: {
    fontSize: "15px",
    lineHeight: 1.7,
    color: "#8899bb",
    marginBottom: "40px",
  },
  heroButtons: {
    display: "flex",
    gap: "12px",
    marginBottom: "32px",
    flexWrap: "wrap",
  },
  primaryButton: {
    padding: "13px 28px",
    background: "#4ecdc4",
    color: "#0d1117",
    border: "none",
    borderRadius: "10px",
    cursor: "pointer",
    fontFamily: "'Clash Display', sans-serif",
    fontSize: "14px",
    fontWeight: 600,
    transition: "transform 0.15s, box-shadow 0.15s",
    ":hover": {
      transform: "translateY(-2px)",
      boxShadow: "0 8px 24px rgba(78,205,196,0.3)",
    },
  },
  secondaryButton: {
    padding: "13px 28px",
    background: "transparent",
    color: "#8899bb",
    border: "1px solid #2d3a52",
    borderRadius: "10px",
    cursor: "pointer",
    fontFamily: "'DM Mono', monospace",
    fontSize: "13px",
    transition: "border-color 0.2s, color 0.2s",
    ":hover": {
      borderColor: "#4ecdc4",
      color: "#4ecdc4",
    },
  },
  techStack: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap",
  },
  techBadge: {
    padding: "6px 12px",
    background: "#161b27",
    border: "1px solid #252f42",
    borderRadius: "8px",
    fontSize: "11px",
    color: "#8899bb",
  },
  authSection: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "40px",
    background: "rgba(13,17,23,0.95)",
    backdropFilter: "blur(10px)",
    borderLeft: "1px solid #252f42",
  },
  authCard: {
    width: "100%",
    maxWidth: "380px",
    padding: "32px",
    background: "#161b27",
    border: "1px solid #252f42",
    borderRadius: "16px",
    boxShadow: "0 20px 40px rgba(0,0,0,0.5)",
  },
  title: {
    margin: "0 0 8px",
    color: "#dde5f4",
    fontSize: "28px",
    fontFamily: "'Clash Display', sans-serif",
    fontWeight: 700,
  },
  subtitle: {
    margin: "0 0 32px",
    color: "#5c7099",
    fontSize: "13px",
    lineHeight: 1.6,
  },
  toggleWrap: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "8px",
    marginBottom: "24px",
    background: "#1c2333",
    padding: "4px",
    borderRadius: "8px",
  },
  toggle: {
    border: "none",
    background: "transparent",
    color: "#5c7099",
    fontWeight: 600,
    borderRadius: "6px",
    padding: "10px",
    cursor: "pointer",
    fontSize: "13px",
    transition: "all 0.2s",
  },
  toggleActive: {
    border: "none",
    background: "#4ecdc4",
    color: "#0d1117",
    fontWeight: 700,
    borderRadius: "6px",
    padding: "10px",
    cursor: "pointer",
    fontSize: "13px",
    boxShadow: "0 2px 8px rgba(78,205,196,0.3)",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  input: {
    border: "1px solid #252f42",
    borderRadius: "8px",
    padding: "12px 16px",
    fontSize: "13px",
    background: "#1c2333",
    color: "#dde5f4",
    outline: "none",
    transition: "border-color 0.2s",
    "::placeholder": {
      color: "#5c7099",
    },
    ":focus": {
      borderColor: "#4ecdc4",
    },
  },
  error: {
    borderRadius: "8px",
    padding: "12px",
    background: "rgba(255,107,107,0.1)",
    border: "1px solid rgba(255,107,107,0.3)",
    color: "#ff6b6b",
    fontSize: "12px",
  },
  submitButton: {
    border: "none",
    borderRadius: "8px",
    padding: "14px",
    fontWeight: 600,
    fontSize: "13px",
    background: "#4ecdc4",
    color: "#0d1117",
    cursor: "pointer",
    marginTop: "8px",
    transition: "all 0.2s",
    fontFamily: "'Clash Display', sans-serif",
    ":hover": {
      transform: "translateY(-1px)",
      boxShadow: "0 4px 12px rgba(78,205,196,0.3)",
    },
    ":disabled": {
      opacity: 0.5,
      cursor: "not-allowed",
    },
  },
  statsBar: {
    marginTop: "24px",
    padding: "16px",
    background: "#1c2333",
    borderRadius: "10px",
    fontSize: "12px",
    color: "#5c7099",
    textAlign: "center",
    border: "1px solid #252f42",
  },
};

export default App;