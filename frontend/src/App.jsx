import React, { useMemo, useState } from "react";
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
          <div>
            <div style={styles.brand}>Memory Graph</div>
            <div style={styles.subtleText}>Signed in as {userId || "user"}</div>
          </div>
          <button type="button" onClick={handleLogout} style={styles.ghostButton}>
            Logout
          </button>
        </header>
        <main style={styles.graphWrap}>
          <GraphPanel token={token} onUnauthorized={handleLogout} />
        </main>
      </div>
    );
  }

  return (
    <div style={styles.authScene}>
      <div style={styles.backGlowOne} />
      <div style={styles.backGlowTwo} />

      <section style={styles.authCard}>
        <h1 style={styles.title}>{title}</h1>
        <p style={styles.subtitle}>
          Authenticate first, then your personal graph visualization loads automatically.
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
            Signup
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

          <button type="submit" style={styles.primaryButton} disabled={loading}>
            {loading ? "Authenticating..." : mode === "login" ? "Login & Open Graph" : "Signup & Open Graph"}
          </button>
        </form>
      </section>
    </div>
  );
}

const styles = {
  appShell: {
    minHeight: "100vh",
    background: "radial-gradient(circle at 15% 20%, #bce7ff 0%, #f5f9ff 38%, #f8eee3 100%)",
    color: "#102333",
    fontFamily: "'Space Grotesk', 'Trebuchet MS', sans-serif",
    padding: "20px",
  },
  topBar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "10px 4px 18px",
  },
  brand: {
    fontSize: "24px",
    fontWeight: 700,
    letterSpacing: "0.03em",
  },
  subtleText: {
    opacity: 0.75,
    fontSize: "13px",
  },
  graphWrap: {
    maxWidth: "1200px",
    margin: "0 auto",
  },
  authScene: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "24px",
    position: "relative",
    overflow: "hidden",
    background: "linear-gradient(140deg, #042f4b 0%, #104f55 45%, #6f8c3a 100%)",
    fontFamily: "'Space Grotesk', 'Trebuchet MS', sans-serif",
  },
  backGlowOne: {
    position: "absolute",
    width: "460px",
    height: "460px",
    borderRadius: "50%",
    background: "rgba(255, 198, 109, 0.35)",
    filter: "blur(45px)",
    top: "-100px",
    right: "-80px",
  },
  backGlowTwo: {
    position: "absolute",
    width: "360px",
    height: "360px",
    borderRadius: "50%",
    background: "rgba(133, 220, 255, 0.35)",
    filter: "blur(50px)",
    bottom: "-100px",
    left: "-70px",
  },
  authCard: {
    position: "relative",
    zIndex: 2,
    width: "100%",
    maxWidth: "460px",
    background: "rgba(255, 255, 255, 0.92)",
    borderRadius: "18px",
    padding: "26px",
    boxShadow: "0 24px 45px rgba(0, 0, 0, 0.24)",
  },
  title: {
    margin: "0 0 8px",
    color: "#0c2f45",
    fontSize: "30px",
    lineHeight: 1.1,
  },
  subtitle: {
    margin: "0 0 18px",
    color: "#334c5c",
    fontSize: "14px",
  },
  toggleWrap: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "8px",
    marginBottom: "14px",
  },
  toggle: {
    border: "1px solid #9bb3c3",
    background: "#f6fbff",
    color: "#2b4250",
    fontWeight: 600,
    borderRadius: "10px",
    padding: "10px",
    cursor: "pointer",
  },
  toggleActive: {
    border: "1px solid #0b6572",
    background: "#0b6572",
    color: "#fff",
    fontWeight: 700,
    borderRadius: "10px",
    padding: "10px",
    cursor: "pointer",
  },
  form: {
    display: "grid",
    gap: "10px",
  },
  input: {
    border: "1px solid #bbcad5",
    borderRadius: "10px",
    padding: "12px",
    fontSize: "15px",
    background: "#fefefe",
  },
  error: {
    borderRadius: "10px",
    padding: "10px",
    background: "#ffebeb",
    color: "#841c1c",
    fontSize: "14px",
  },
  primaryButton: {
    border: "none",
    borderRadius: "12px",
    padding: "12px 14px",
    fontWeight: 700,
    background: "linear-gradient(100deg, #1469c4, #1f90b2)",
    color: "#fff",
    cursor: "pointer",
  },
  ghostButton: {
    border: "1px solid #5a7a90",
    background: "rgba(255, 255, 255, 0.65)",
    borderRadius: "10px",
    padding: "8px 14px",
    cursor: "pointer",
    color: "#17384d",
    fontWeight: 600,
  },
};

export default App;
