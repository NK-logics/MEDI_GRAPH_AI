import React, { useEffect, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";

function GraphPanel({ token, onUnauthorized }) {
  const [graphData, setGraphData] = useState({
    nodes: [],
    links: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");

    fetch("/graph", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (res) => {
        const data = await res.json();
        return { ok: res.ok, status: res.status, data };
      })
      .then((data) => {
        if (!data.ok && data.status === 401) {
          onUnauthorized?.();
          return;
        }
        if (!data.ok) {
          throw new Error(data.data?.detail || "Could not load graph.");
        }
        if (data.data?.error) {
          throw new Error(data.data.error);
        }

        const nodes = Array.isArray(data.data?.nodes) ? data.data.nodes : [];
        const edges = Array.isArray(data.data?.edges) ? data.data.edges : [];

        const formatted = {
          nodes,
          links: edges.map((edge) => ({
            source: edge.from,
            target: edge.to,
            label: edge.label,
          })),
        };

        setGraphData(formatted);
        setLoading(false);
      })
      .catch((err) => {
        setGraphData({ nodes: [], links: [] });
        setError(err.message || "Could not load graph.");
        setLoading(false);
      });
  }, [token, onUnauthorized]);

  if (loading) {
    return <div style={{ padding: "18px", color: "#274357" }}>Loading your graph...</div>;
  }

  if (error) {
    return <div style={{ padding: "18px", color: "#8a1f1f" }}>{error}</div>;
  }

  return (
    <div style={{ height: "74vh", minHeight: "500px", background: "rgba(255,255,255,0.55)", borderRadius: "16px" }}>
      <ForceGraph2D
        graphData={graphData}
        nodeLabel="label"
        linkLabel="label"
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.label ?? String(node.id);
          const fontSize = 14 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";

          ctx.fillStyle = "#1f77b4";
          ctx.beginPath();
          ctx.arc(node.x, node.y, 7, 0, 2 * Math.PI, false);
          ctx.fill();

          ctx.fillStyle = "#111";
          ctx.fillText(label, node.x, node.y - 12);
        }}
        linkCanvasObjectMode={() => "after"}
        linkCanvasObject={(link, ctx, globalScale) => {
          const label = link.label;
          if (!label) return;

          const start = link.source;
          const end = link.target;
          if (typeof start !== "object" || typeof end !== "object") return;

          const fontSize = 12 / globalScale;
          const text = String(label);
          const midX = (start.x + end.x) / 2;
          const midY = (start.y + end.y) / 2;

          ctx.font = `${fontSize}px Sans-Serif`;
          const textWidth = ctx.measureText(text).width;
          const padding = 2 / globalScale;

          ctx.fillStyle = "rgba(255,255,255,0.85)";
          ctx.fillRect(
            midX - textWidth / 2 - padding,
            midY - fontSize / 2 - padding,
            textWidth + padding * 2,
            fontSize + padding * 2,
          );

          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillStyle = "#333";
          ctx.fillText(text, midX, midY);
        }}
      />
    </div>
  );
}

export default GraphPanel;
