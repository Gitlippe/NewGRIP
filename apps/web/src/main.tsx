import React, { Component, ReactNode } from "react";
import ReactDOM from "react-dom/client";
import "reactflow/dist/style.css";
import { App } from "./App";
import "./styles.css";

type EBState = { error: Error | null };

class ErrorBoundary extends Component<{ children: ReactNode }, EBState> {
  state: EBState = { error: null };
  static getDerivedStateFromError(error: Error) { return { error }; }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 40, color: "#e7edf5", background: "#0a0f1a", height: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <h1 style={{ fontSize: 20, marginBottom: 12 }}>Something went wrong</h1>
          <pre style={{ fontSize: 13, color: "#f87171", maxWidth: 600, overflow: "auto" }}>{this.state.error.message}</pre>
          <button onClick={() => this.setState({ error: null })} style={{ marginTop: 20, padding: "8px 20px", background: "#1e3a5f", border: "1px solid #3b82f6", borderRadius: 6, color: "#e7edf5", cursor: "pointer" }}>
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
);
