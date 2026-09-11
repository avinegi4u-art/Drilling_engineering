"use strict";

// Declarative definition of every calculator card rendered on the page.
const CALCULATORS = [
  {
    id: "hydrostatic-pressure",
    title: "Hydrostatic Pressure",
    icon: "\u2193",
    desc: "Bottom-hole pressure from a static mud column. P = 0.052 \u00d7 MW \u00d7 TVD.",
    endpoint: "/api/hydrostatic-pressure",
    fields: [
      { name: "mud_weight_ppg", label: "Mud weight (ppg)", value: 9.5 },
      { name: "tvd_ft", label: "TVD (ft)", value: 10000 },
    ],
  },
  {
    id: "ecd",
    title: "Equivalent Circulating Density",
    icon: "\u21bb",
    desc: "Effective density while circulating. ECD = MW + APL / (0.052 \u00d7 TVD).",
    endpoint: "/api/ecd",
    fields: [
      { name: "mud_weight_ppg", label: "Mud weight (ppg)", value: 9.5 },
      {
        name: "annular_pressure_loss_psi",
        label: "Annular pressure loss (psi)",
        value: 250,
      },
      { name: "tvd_ft", label: "TVD (ft)", value: 10000 },
    ],
  },
  {
    id: "buoyancy-factor",
    title: "Buoyancy Factor",
    icon: "\u2696",
    desc: "String weight reduction in mud. BF = (65.5 \u2212 MW) / 65.5.",
    endpoint: "/api/buoyancy-factor",
    fields: [{ name: "mud_weight_ppg", label: "Mud weight (ppg)", value: 12.0 }],
  },
  {
    id: "annular-velocity",
    title: "Annular Velocity",
    icon: "\u2191",
    desc: "Fluid velocity in the annulus. AV = 24.51 \u00d7 Q / (Dh\u00b2 \u2212 Dp\u00b2).",
    endpoint: "/api/annular-velocity",
    fields: [
      { name: "flow_rate_gpm", label: "Flow rate (gpm)", value: 500 },
      { name: "hole_diameter_in", label: "Hole diameter (in)", value: 8.5 },
      { name: "pipe_diameter_in", label: "Pipe diameter (in)", value: 5.0 },
    ],
  },
  {
    id: "dogleg-severity",
    title: "Dogleg Severity",
    icon: "\u2197",
    desc: "Wellbore curvature between two survey stations (minimum curvature).",
    endpoint: "/api/dogleg-severity",
    fields: [
      { name: "inclination_1_deg", label: "Inclination 1 (deg)", value: 15 },
      { name: "azimuth_1_deg", label: "Azimuth 1 (deg)", value: 20 },
      { name: "inclination_2_deg", label: "Inclination 2 (deg)", value: 25 },
      { name: "azimuth_2_deg", label: "Azimuth 2 (deg)", value: 45 },
      { name: "course_length_ft", label: "Course length (ft)", value: 100 },
    ],
  },
  {
    id: "kill-mud-weight",
    title: "Kill Mud Weight",
    icon: "\u26d1",
    desc: "Mud weight to balance formation pressure after a kick. KMW = MW + SIDPP / (0.052 \u00d7 TVD).",
    endpoint: "/api/kill-mud-weight",
    fields: [
      { name: "current_mud_weight_ppg", label: "Current mud weight (ppg)", value: 9.5 },
      { name: "sidpp_psi", label: "SIDPP (psi)", value: 300 },
      { name: "tvd_ft", label: "TVD (ft)", value: 10000 },
    ],
  },
];

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else node.setAttribute(k, v);
  });
  (Array.isArray(children) ? children : [children]).forEach((c) =>
    node.appendChild(c)
  );
  return node;
}

function buildCard(spec) {
  const inputs = {};
  const fieldNodes = spec.fields.map((f) => {
    const input = el("input", {
      type: "number",
      step: "any",
      value: String(f.value),
      id: `${spec.id}-${f.name}`,
    });
    inputs[f.name] = input;
    return el("div", { class: "field" }, [
      el("label", { for: input.id, text: f.label }),
      input,
    ]);
  });

  const result = el("div", { class: "result", text: "\u2014" });
  const button = el("button", { class: "calc", type: "button", text: "Calculate" });

  button.addEventListener("click", async () => {
    const payload = {};
    for (const [name, input] of Object.entries(inputs)) {
      payload[name] = parseFloat(input.value);
    }
    result.className = "result";
    result.textContent = "Calculating\u2026";
    try {
      const res = await fetch(spec.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg).join("; ")
          : data.detail || "Invalid input";
        result.className = "result err";
        result.textContent = detail;
        return;
      }
      result.className = "result ok";
      result.textContent = `${data.value} ${data.unit}`;
    } catch (err) {
      result.className = "result err";
      result.textContent = `Request failed: ${err.message}`;
    }
  });

  return el("section", { class: "card", id: `card-${spec.id}` }, [
    el("h2", {}, [
      el("span", { text: spec.icon, "aria-hidden": "true" }),
      el("span", { text: spec.title }),
    ]),
    el("p", { class: "desc", text: spec.desc }),
    ...fieldNodes,
    button,
    result,
  ]);
}

async function checkHealth() {
  const pill = document.getElementById("api-status");
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    if (res.ok && data.status === "ok") {
      pill.className = "status-pill status-ok";
      pill.textContent = `API online \u00b7 v${data.version}`;
      return;
    }
    throw new Error("unhealthy");
  } catch {
    pill.className = "status-pill status-err";
    pill.textContent = "API offline";
  }
}

function main() {
  const container = document.getElementById("calculators");
  CALCULATORS.forEach((spec) => container.appendChild(buildCard(spec)));
  checkHealth();
}

document.addEventListener("DOMContentLoaded", main);
