const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// Icon helper
async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

// Color Palette — Deep Midnight Tech (crypto/finance vibe)
const C = {
  darkBg: "0D1117",   // near-black for title/section slides
  midBg: "161B22",   // slightly lighter dark panel
  cardBg: "1E2940",   // card surface (dark navy)
  cardLight: "21325A",   // slightly lighter card
  accent: "00D4FF",   // bright cyan accent
  accent2: "7C3AED",   // purple accent
  gold: "F59E0B",   // amber/gold highlight
  green: "10B981",   // risk-low green
  red: "EF4444",   // risk-high red
  yellow: "F59E0B",   // risk-medium
  white: "FFFFFF",
  offWhite: "E2E8F0",
  muted: "94A3B8",
  mutedDim: "64748B",
  lightBg: "F0F4F8",   // light content slides
  lightCard: "FFFFFF",
  textDark: "1E293B",
  textMid: "334155",
};

async function buildPresentation() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "AI-Based Cryptocurrency Market Behavior Analyzer and Risk Predictor";

  // ─────────────────────────────────────────────────────────────
  // SLIDE 1 — TITLE SLIDE (dark)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.darkBg };

    // Top geometric accent — circuit-board style circles
    sl.addShape(pres.shapes.OVAL, { x: 8.5, y: -0.4, w: 2.2, h: 2.2, fill: { color: C.accent2, transparency: 85 }, line: { color: C.accent2, width: 1, transparency: 70 } });
    sl.addShape(pres.shapes.OVAL, { x: 8.9, y: -0.1, w: 1.4, h: 1.4, fill: { color: C.accent, transparency: 90 }, line: { color: C.accent, width: 1, transparency: 60 } });
    sl.addShape(pres.shapes.OVAL, { x: -0.3, y: 4.5, w: 1.8, h: 1.8, fill: { color: C.accent2, transparency: 88 }, line: { color: C.accent2, width: 1 } });

    // Cyan accent block on left edge
    sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 1.8, w: 0.07, h: 2.0, fill: { color: C.accent } });

    // Title text
    sl.addText("AI-Based Cryptocurrency", {
      x: 0.4, y: 1.0, w: 9.2, h: 0.75,
      fontSize: 38, bold: true, color: C.white,
      fontFace: "Calibri", align: "left", margin: 0
    });
    sl.addText("Market Behavior Analyzer", {
      x: 0.4, y: 1.75, w: 9.2, h: 0.75,
      fontSize: 38, bold: true, color: C.white,
      fontFace: "Calibri", align: "left", margin: 0
    });
    sl.addText("& Risk Predictor", {
      x: 0.4, y: 2.5, w: 9.2, h: 0.65,
      fontSize: 34, bold: true, color: C.accent,
      fontFace: "Calibri", align: "left", margin: 0
    });

    // Subtitle line
    sl.addText("Term Project Presentation", {
      x: 0.4, y: 3.3, w: 9.2, h: 0.35,
      fontSize: 14, color: C.muted,
      fontFace: "Calibri", align: "left", margin: 0, italic: true
    });

    // Divider
    sl.addShape(pres.shapes.LINE, { x: 0.4, y: 3.8, w: 9.2, h: 0, line: { color: C.mutedDim, width: 0.5 } });

    // Team info
    sl.addText([
      { text: "Presented by:  ", options: { color: C.muted, fontSize: 12 } },
      { text: "Adan Mehmood  •  Hashir Rehman  •  Waseem Anwar", options: { color: C.offWhite, fontSize: 12, bold: true } }
    ], { x: 0.4, y: 4.0, w: 9.2, h: 0.3, fontFace: "Calibri", align: "left", margin: 0 });

    sl.addText([
      { text: "Submitted to:  ", options: { color: C.muted, fontSize: 12 } },
      { text: "[Professor Name]", options: { color: C.offWhite, fontSize: 12 } },
      { text: "          Date:  ", options: { color: C.muted, fontSize: 12 } },
      { text: "[Date of Presentation]", options: { color: C.offWhite, fontSize: 12 } }
    ], { x: 0.4, y: 4.4, w: 9.2, h: 0.3, fontFace: "Calibri", align: "left", margin: 0 });

    sl.addNotes("Speaker 1: Introduce the team and welcome the panel. Set the stage for what we built.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 2 — INTRODUCTION & PROBLEM STATEMENT (dark)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.darkBg };

    // Slide number badge
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("02", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    // Title
    sl.addText("Introduction & Problem Statement", {
      x: 0.5, y: 0.3, w: 8.7, h: 0.55,
      fontSize: 28, bold: true, color: C.white,
      fontFace: "Calibri", align: "left", margin: 0
    });

    // Context card
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: 1.05, w: 8.8, h: 0.6,
      fill: { color: C.cardBg }, rectRadius: 0.1,
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 45, opacity: 0.3 }
    });
    sl.addText([
      { text: "Context: ", options: { bold: true, color: C.accent } },
      { text: "Cryptocurrency markets operate 24/7 and are highly volatile — demanding real-time intelligence.", options: { color: C.offWhite } }
    ], { x: 0.7, y: 1.05, w: 8.4, h: 0.6, fontSize: 13, fontFace: "Calibri", valign: "middle", margin: 0 });

    // Problems — 3 cards
    sl.addText("The Problem", { x: 0.5, y: 1.85, w: 3.5, h: 0.35, fontSize: 15, bold: true, color: C.accent, fontFace: "Calibri", margin: 0 });

    const problems = [
      { icon: "⚡", title: "Extreme Volatility", desc: "Wild price swings and unpredictable market conditions make manual monitoring impossible." },
      { icon: "📊", title: "Information Asymmetry", desc: "Retail investors lack tools to properly assess risk compared to institutional traders." },
      { icon: "🤖", title: "No Unified AI Tool", desc: "No reliable platform combines traditional indicators with machine learning-driven predictions." },
    ];

    problems.forEach((p, i) => {
      const x = 0.5 + i * 3.1;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 2.25, w: 2.95, h: 1.4,
        fill: { color: C.cardBg }, rectRadius: 0.1,
        shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 45, opacity: 0.25 }
      });
      sl.addText(p.icon, { x, y: 2.3, w: 2.95, h: 0.4, fontSize: 22, align: "center", margin: 0, fontFace: "Calibri" });
      sl.addText(p.title, { x, y: 2.72, w: 2.95, h: 0.3, fontSize: 13, bold: true, color: C.accent, align: "center", margin: 0, fontFace: "Calibri" });
      sl.addText(p.desc, { x: x + 0.1, y: 3.05, w: 2.75, h: 0.55, fontSize: 10, color: C.muted, align: "center", margin: 0, fontFace: "Calibri" });
    });

    // Solution banner
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: 3.8, w: 8.8, h: 0.75,
      fill: { color: "0D2140" }, rectRadius: 0.1
    });
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: 3.8, w: 8.8, h: 0.75,
      fill: { color: C.accent, transparency: 92 }, rectRadius: 0.1
    });
    sl.addText([
      { text: "Our Solution:  ", options: { bold: true, color: C.accent } },
      { text: "A comprehensive AI-driven platform combining trend prediction, risk classification, and intelligent trading recommendations.", options: { color: C.white } }
    ], { x: 0.7, y: 3.8, w: 8.4, h: 0.75, fontSize: 12, fontFace: "Calibri", valign: "middle", margin: 0 });

    sl.addNotes("Speaker 1: Describe the market chaos. Explain why retail investors are at a disadvantage. Then reveal our solution.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 3 — PROJECT OBJECTIVES (light)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.lightBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("03", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Project Objectives", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 28, bold: true, color: C.textDark, fontFace: "Calibri", align: "left", margin: 0
    });

    const objectives = [
      { num: "01", title: "Automate Data Collection", desc: "Fetch live OHLCV data from Binance API with fallback to Yahoo Finance for high availability.", color: C.accent },
      { num: "02", title: "Feature Engineering", desc: "Calculate SMA, EMA, RSI, MACD, and Bollinger Bands for comprehensive market analysis.", color: C.accent2 },
      { num: "03", title: "Predictive Modeling", desc: "Train Random Forest & Logistic Regression models to predict Bullish/Bearish trends.", color: C.gold },
      { num: "04", title: "Risk Classification", desc: "Implement K-Means Clustering to segment market into Low, Medium, and High risk levels.", color: C.green },
      { num: "05", title: "Intelligent Agent", desc: "Build a rule-based BUY/SELL/HOLD recommendation engine powered by AI predictions.", color: "EF4444" },
      { num: "06", title: "Interactive Dashboard", desc: "Develop a Streamlit web interface for live monitoring, charts, and insights.", color: "8B5CF6" },
    ];

    objectives.forEach((obj, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = 0.5 + col * 4.85;
      const y = 1.05 + row * 1.35;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y, w: 4.55, h: 1.2,
        fill: { color: C.white }, rectRadius: 0.1,
        shadow: { type: "outer", color: "000000", blur: 5, offset: 2, angle: 45, opacity: 0.08 }
      });
      // Numbered badge
      sl.addShape(pres.shapes.OVAL, { x: x + 0.12, y: y + 0.12, w: 0.5, h: 0.5, fill: { color: obj.color } });
      sl.addText(obj.num, { x: x + 0.12, y: y + 0.12, w: 0.5, h: 0.5, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });
      // Content
      sl.addText(obj.title, { x: x + 0.75, y: y + 0.1, w: 3.7, h: 0.35, fontSize: 13, bold: true, color: C.textDark, margin: 0, fontFace: "Calibri" });
      sl.addText(obj.desc, { x: x + 0.75, y: y + 0.45, w: 3.7, h: 0.65, fontSize: 10.5, color: C.textMid, margin: 0, fontFace: "Calibri" });
    });

    sl.addNotes("Speaker 1: Walk through each objective. Emphasize the modular design — each objective builds on the previous one.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 4 — TECHNOLOGY STACK (dark)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.darkBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("04", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Technology Stack", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 28, bold: true, color: C.white, fontFace: "Calibri", align: "left", margin: 0
    });

    const techs = [
      { label: "Python 3.10+", role: "Core Language", color: C.accent, emoji: "🐍" },
      { label: "Streamlit", role: "Frontend UI Dashboard", color: C.accent2, emoji: "🖥️" },
      { label: "Scikit-learn", role: "ML: RF, LR, K-Means", color: C.gold, emoji: "⚙️" },
      { label: "Pandas & NumPy", role: "Data Manipulation", color: C.green, emoji: "📐" },
      { label: "ta Library", role: "Technical Indicators", color: "EF4444", emoji: "📈" },
      { label: "Plotly", role: "Interactive Visualizations", color: "8B5CF6", emoji: "📊" },
      { label: "Binance API", role: "Primary Data Source", color: "F97316", emoji: "🔗" },
      { label: "yfinance", role: "Fallback Data Source", color: "06B6D4", emoji: "📡" },
    ];

    techs.forEach((t, i) => {
      const col = i % 4;
      const row = Math.floor(i / 4);
      const x = 0.4 + col * 2.32;
      const y = 1.05 + row * 2.0;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y, w: 2.1, h: 1.75,
        fill: { color: C.cardBg }, rectRadius: 0.12,
        shadow: { type: "outer", color: "000000", blur: 10, offset: 3, angle: 45, opacity: 0.35 }
      });
      // Color band at top of card  → replaced with top-tinted background approach
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: x + 0.1, y: y + 0.1, w: 1.9, h: 0.55,
        fill: { color: t.color, transparency: 80 }, rectRadius: 0.08
      });
      sl.addText(t.emoji, { x: x + 0.1, y: y + 0.12, w: 1.9, h: 0.5, fontSize: 22, align: "center", margin: 0, fontFace: "Calibri" });
      sl.addText(t.label, { x: x + 0.1, y: y + 0.72, w: 1.9, h: 0.45, fontSize: 12, bold: true, color: C.white, align: "center", margin: 0, fontFace: "Calibri" });
      sl.addText(t.role, { x: x + 0.1, y: y + 1.18, w: 1.9, h: 0.45, fontSize: 9.5, color: C.muted, align: "center", margin: 0, fontFace: "Calibri" });
    });

    sl.addNotes("Speaker 1: Briefly explain each tool and why we chose it. Emphasize Python ecosystem and Streamlit for rapid deployment.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 5 — SYSTEM ARCHITECTURE (light)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.lightBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("05", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("System Architecture Overview", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 28, bold: true, color: C.textDark, fontFace: "Calibri", align: "left", margin: 0
    });

    // Architecture flow diagram — 4 horizontal layers
    const layers = [
      { title: "Data Layer", items: "Binance API  •  yfinance Fallback  •  Cleaner  •  Feature Engineer", color: "0D9488" },
      { title: "Service Layer", items: "REST API Integrations  •  Error Handling  •  Rate Limiting  •  Caching", color: "7C3AED" },
      { title: "ML Models Layer", items: "Random Forest  •  Logistic Regression  •  K-Means Clustering  •  joblib Versioning", color: "B45309" },
      { title: "Intelligent Agent", items: "Probability Synthesizer  •  Risk Evaluator  •  BUY/SELL/HOLD Engine", color: "DC2626" },
    ];

    layers.forEach((layer, i) => {
      const y = 0.95 + i * 0.86;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.5, y, w: 9.0, h: 0.72,
        fill: { color: layer.color, transparency: 88 }, rectRadius: 0.08,
        shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 45, opacity: 0.1 }
      });
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.5, y, w: 1.8, h: 0.72,
        fill: { color: layer.color, transparency: 15 }, rectRadius: 0.08
      });
      sl.addText(layer.title, { x: 0.55, y, w: 1.7, h: 0.72, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });
      sl.addText(layer.items, { x: 2.45, y, w: 6.9, h: 0.72, fontSize: 11.5, color: C.textMid, valign: "middle", margin: 0, fontFace: "Calibri" });
      // Downward arrow between layers
      sl.addShape(pres.shapes.LINE, { x: 4.85, y: y + 0.72, w: 0, h: 0.14, line: { color: "94A3B8", width: 1.5 } });
      sl.addText("▼", { x: 4.6, y: y + 0.73, w: 0.5, h: 0.12, fontSize: 9, color: "94A3B8", align: "center", margin: 0, fontFace: "Calibri" });
    });

    // Frontend layer at bottom
    const y5 = 0.95 + 4 * 0.86;
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: y5, w: 9.0, h: 0.72,
      fill: { color: "065A82", transparency: 85 }, rectRadius: 0.08,
      shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 45, opacity: 0.1 }
    });
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: y5, w: 1.8, h: 0.72,
      fill: { color: "065A82", transparency: 15 }, rectRadius: 0.08
    });
    sl.addText("Frontend UI", { x: 0.55, y: y5, w: 1.7, h: 0.72, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });
    sl.addText("Streamlit Multi-Page App  •  Live Charts  •  Prediction Dashboard  •  Performance Metrics", { x: 2.45, y: y5, w: 6.9, h: 0.72, fontSize: 11.5, color: C.textMid, valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addNotes("Speaker 2: Walk through the architecture from bottom (data) to top (UI). Emphasize modularity and the fallback mechanism.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 6 — DATA PIPELINE & FEATURE ENGINEERING (dark)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.darkBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("06", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Data Pipeline & Feature Engineering", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 26, bold: true, color: C.white, fontFace: "Calibri", align: "left", margin: 0
    });

    // Pipeline steps (left column)
    sl.addText("Pipeline Steps", { x: 0.5, y: 1.0, w: 4.5, h: 0.35, fontSize: 14, bold: true, color: C.accent, margin: 0, fontFace: "Calibri" });

    const steps = [
      { step: "1", label: "Data Collection", desc: "Live REST API calls — OHLCV data (Open, High, Low, Close, Volume)" },
      { step: "2", label: "Preprocessing", desc: "Handle missing values, remove outliers, standardize features" },
      { step: "3", label: "Feature Engineering", desc: "Derive technical indicators from raw price data" },
      { step: "4", label: "Target Labeling", desc: "Next day Close > Today? → 1 (Bullish) : 0 (Bearish)" },
    ];

    steps.forEach((s, i) => {
      const y = 1.45 + i * 0.95;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.5, y, w: 4.5, h: 0.8, fill: { color: C.cardBg }, rectRadius: 0.08,
        shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 45, opacity: 0.25 }
      });
      sl.addShape(pres.shapes.OVAL, { x: 0.6, y: y + 0.15, w: 0.45, h: 0.45, fill: { color: C.accent } });
      sl.addText(s.step, { x: 0.6, y: y + 0.15, w: 0.45, h: 0.45, fontSize: 12, bold: true, color: C.darkBg, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });
      sl.addText(s.label, { x: 1.15, y: y + 0.05, w: 3.75, h: 0.3, fontSize: 12, bold: true, color: C.white, margin: 0, fontFace: "Calibri" });
      sl.addText(s.desc, { x: 1.15, y: y + 0.38, w: 3.75, h: 0.35, fontSize: 10, color: C.muted, margin: 0, fontFace: "Calibri" });
    });

    // Feature Engineering detail (right column)
    sl.addText("Engineered Features", { x: 5.3, y: 1.0, w: 4.4, h: 0.35, fontSize: 14, bold: true, color: C.gold, margin: 0, fontFace: "Calibri" });

    const features = [
      { cat: "📈 Trend", items: "SMA, EMA, MACD", color: "0D9488" },
      { cat: "⚡ Momentum", items: "Relative Strength Index (RSI)", color: "7C3AED" },
      { cat: "🌀 Volatility", items: "Bollinger Bands, Rolling Std Dev", color: C.gold },
    ];

    features.forEach((f, i) => {
      const y = 1.45 + i * 1.05;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 5.3, y, w: 4.4, h: 0.9, fill: { color: C.cardBg }, rectRadius: 0.08,
        shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 45, opacity: 0.25 }
      });
      sl.addText(f.cat, { x: 5.5, y: y + 0.08, w: 4.0, h: 0.35, fontSize: 13, bold: true, color: C.white, margin: 0, fontFace: "Calibri" });
      sl.addText(f.items, { x: 5.5, y: y + 0.45, w: 4.0, h: 0.35, fontSize: 11, color: C.muted, margin: 0, fontFace: "Calibri" });
    });

    sl.addNotes("Speaker 2: Explain OHLCV, why these indicators matter, and how we label targets for supervised learning.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 7 — PREDICTIVE MODELING (light)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.lightBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("07", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Predictive Modeling", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 28, bold: true, color: C.textDark, fontFace: "Calibri", align: "left", margin: 0
    });

    // Left card — Random Forest
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: 1.0, w: 4.5, h: 4.2,
      fill: { color: C.white }, rectRadius: 0.12,
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 45, opacity: 0.1 }
    });
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: 1.0, w: 4.5, h: 0.6,
      fill: { color: "0D9488", transparency: 10 }, rectRadius: 0.12
    });
    sl.addText("🌳  Random Forest", { x: 0.6, y: 1.0, w: 4.3, h: 0.6, fontSize: 15, bold: true, color: C.white, valign: "middle", margin: 0, fontFace: "Calibri" });
    sl.addText("Primary Model", { x: 0.6, y: 1.62, w: 4.2, h: 0.3, fontSize: 11, color: "0D9488", bold: true, italic: true, margin: 0, fontFace: "Calibri" });

    const rfPoints = [
      "Ensemble learning prevents overfitting on noisy financial data.",
      "Cross-validated using TimeSeriesSplit to preserve chronological order.",
      "Feature Importance reveals RSI and Volatility as top drivers.",
      "Outputs a Bullish vs. Bearish probability score.",
    ];
    rfPoints.forEach((pt, i) => {
      sl.addText([
        { text: "▶  ", options: { color: "0D9488", bold: true } },
        { text: pt, options: { color: C.textMid } }
      ], { x: 0.65, y: 2.0 + i * 0.7, w: 4.2, h: 0.6, fontSize: 11, margin: 0, fontFace: "Calibri" });
    });

    // Right card — Logistic Regression
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 5.2, y: 1.0, w: 4.5, h: 4.2,
      fill: { color: C.white }, rectRadius: 0.12,
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 45, opacity: 0.1 }
    });
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 5.2, y: 1.0, w: 4.5, h: 0.6,
      fill: { color: C.accent2, transparency: 10 }, rectRadius: 0.12
    });
    sl.addText("📉  Logistic Regression", { x: 5.3, y: 1.0, w: 4.3, h: 0.6, fontSize: 15, bold: true, color: C.white, valign: "middle", margin: 0, fontFace: "Calibri" });
    sl.addText("Baseline Model", { x: 5.3, y: 1.62, w: 4.2, h: 0.3, fontSize: 11, color: C.accent2, bold: true, italic: true, margin: 0, fontFace: "Calibri" });

    const lrPoints = [
      "Serves as a performance baseline to benchmark against Random Forest.",
      "Fast training time and highly interpretable coefficients.",
      "Produces calibrated Bullish/Bearish probability output.",
      "Enables side-by-side comparison in the dashboard.",
    ];
    lrPoints.forEach((pt, i) => {
      sl.addText([
        { text: "▶  ", options: { color: C.accent2, bold: true } },
        { text: pt, options: { color: C.textMid } }
      ], { x: 5.35, y: 2.0 + i * 0.7, w: 4.2, h: 0.6, fontSize: 11, margin: 0, fontFace: "Calibri" });
    });

    sl.addNotes("Speaker 2: Explain why we chose Random Forest as primary and why Logistic Regression as baseline. Mention TimeSeriesSplit.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 8 — RISK CLASSIFICATION (dark)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.darkBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("08", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Risk Classification — K-Means Clustering", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 24, bold: true, color: C.white, fontFace: "Calibri", align: "left", margin: 0
    });

    // Methodology card
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: 1.0, w: 5.5, h: 1.3, fill: { color: C.cardBg }, rectRadius: 0.1,
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 45, opacity: 0.3 }
    });
    sl.addText("Unsupervised Learning Approach", { x: 0.7, y: 1.05, w: 5.0, h: 0.35, fontSize: 13, bold: true, color: C.accent, margin: 0, fontFace: "Calibri" });
    sl.addText([
      { text: "K-Means Clustering (k=3)", options: { bold: true, color: C.white } },
      { text: " segments the live market state into three distinct risk zones using unsupervised learning — no labels needed.", options: { color: C.muted } }
    ], { x: 0.7, y: 1.42, w: 5.1, h: 0.75, fontSize: 11, margin: 0, fontFace: "Calibri" });

    // Features used
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: 2.45, w: 5.5, h: 0.9, fill: { color: C.cardBg }, rectRadius: 0.1,
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 45, opacity: 0.3 }
    });
    sl.addText("Features Used for Clustering:", { x: 0.7, y: 2.5, w: 5.0, h: 0.3, fontSize: 12, bold: true, color: C.gold, margin: 0, fontFace: "Calibri" });
    sl.addText("Rolling Volatility  •  RSI  •  Volume Change  •  Daily Return Std Dev", { x: 0.7, y: 2.82, w: 5.1, h: 0.4, fontSize: 11, color: C.muted, margin: 0, fontFace: "Calibri" });

    // Evaluation
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 3.5, w: 5.5, h: 0.7, fill: { color: C.cardBg }, rectRadius: 0.1 });
    sl.addText([
      { text: "Validation: ", options: { bold: true, color: C.accent } },
      { text: "Silhouette Score + Elbow Method confirmed k=3 as optimal.", options: { color: C.muted } }
    ], { x: 0.7, y: 3.5, w: 5.1, h: 0.7, fontSize: 11, valign: "middle", margin: 0, fontFace: "Calibri" });

    // Three risk clusters — right side
    const clusters = [
      { level: "Low Risk", icon: "🟢", desc: "Stable volatility, RSI in normal range (40-60). Safe market conditions.", color: C.green, textColor: C.green },
      { level: "Medium Risk", icon: "🟡", desc: "Moderate volatility, RSI slightly elevated. Monitor closely.", color: "D97706", textColor: C.gold },
      { level: "High Risk", icon: "🔴", desc: "Extreme volatility, RSI overbought/oversold. Caution required.", color: "DC2626", textColor: "EF4444" },
    ];

    clusters.forEach((c, i) => {
      const y = 1.0 + i * 1.25;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 6.3, y, w: 3.5, h: 1.1, fill: { color: C.cardBg }, rectRadius: 0.1,
        shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 45, opacity: 0.3 }
      });
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.3, y, w: 3.5, h: 1.1, fill: { color: c.color, transparency: 92 }, rectRadius: 0.1 });
      sl.addText(c.icon + "  " + c.level, { x: 6.45, y: y + 0.08, w: 3.2, h: 0.35, fontSize: 13, bold: true, color: c.textColor, margin: 0, fontFace: "Calibri" });
      sl.addText(c.desc, { x: 6.45, y: y + 0.45, w: 3.2, h: 0.55, fontSize: 10, color: C.muted, margin: 0, fontFace: "Calibri" });
    });

    sl.addNotes("Speaker 3: Explain K-Means in simple terms — it's like sorting the market into buckets. Cover features used and validation.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 9 — INTELLIGENT RECOMMENDATION AGENT (light)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.lightBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("09", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Intelligent Recommendation Agent", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 26, bold: true, color: C.textDark, fontFace: "Calibri", align: "left", margin: 0
    });

    // Brain description
    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: 1.0, w: 9.0, h: 0.6, fill: { color: C.white }, rectRadius: 0.08,
      shadow: { type: "outer", color: "000000", blur: 4, offset: 2, angle: 45, opacity: 0.08 }
    });
    sl.addText([
      { text: "🧠  The Brain: ", options: { bold: true, color: C.textDark } },
      { text: "Synthesizes ML trend probabilities + K-Means risk cluster → Actionable trading recommendation.", options: { color: C.textMid } }
    ], { x: 0.7, y: 1.0, w: 8.6, h: 0.6, fontSize: 12, valign: "middle", margin: 0, fontFace: "Calibri" });

    // Rule examples — left
    sl.addText("Rule-Based Engine", { x: 0.5, y: 1.75, w: 5.5, h: 0.35, fontSize: 13, bold: true, color: C.textDark, margin: 0, fontFace: "Calibri" });

    const rules = [
      { cond: "Bullish Prob > 70% AND Risk = Low/Medium", action: "BUY", color: C.green },
      { cond: "Bearish Prob > 60% OR Risk = High", action: "SELL", color: "EF4444" },
      { cond: "Prob between 40–60% OR Mixed signals", action: "HOLD", color: C.gold },
    ];

    rules.forEach((r, i) => {
      const y = 2.15 + i * 0.85;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.5, y, w: 5.5, h: 0.7, fill: { color: r.color, transparency: 92 }, rectRadius: 0.08,
        shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 45, opacity: 0.08 }
      });
      sl.addText([
        { text: "IF ", options: { bold: true, color: C.textMid, fontSize: 10 } },
        { text: r.cond, options: { color: C.textMid, fontSize: 10 } },
        { text: "  ➡  ", options: { bold: true, color: C.textDark, fontSize: 11 } },
        { text: r.action, options: { bold: true, color: r.color, fontSize: 14 } },
      ], { x: 0.65, y, w: 5.2, h: 0.7, valign: "middle", margin: 0, fontFace: "Calibri" });
    });

    // Outputs — right
    sl.addText("Agent Outputs", { x: 6.2, y: 1.75, w: 3.6, h: 0.35, fontSize: 13, bold: true, color: C.textDark, margin: 0, fontFace: "Calibri" });

    const outputs = [
      { label: "Action", value: "BUY  /  SELL  /  HOLD" },
      { label: "Confidence", value: "High  /  Medium  /  Low" },
      { label: "Reasoning", value: "Human-readable explanation" },
      { label: "Risk Tools", value: "Stop-Loss & Take-Profit points" },
    ];

    outputs.forEach((o, i) => {
      const y = 2.15 + i * 0.83;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 6.2, y, w: 3.6, h: 0.68, fill: { color: C.white }, rectRadius: 0.08,
        shadow: { type: "outer", color: "000000", blur: 4, offset: 2, angle: 45, opacity: 0.08 }
      });
      sl.addText(o.label, { x: 6.35, y: y + 0.05, w: 3.2, h: 0.27, fontSize: 9.5, bold: true, color: C.mutedDim, margin: 0, fontFace: "Calibri" });
      sl.addText(o.value, { x: 6.35, y: y + 0.33, w: 3.2, h: 0.27, fontSize: 11.5, bold: true, color: C.textDark, margin: 0, fontFace: "Calibri" });
    });

    sl.addNotes("Speaker 3: Walk through the decision logic. Use the BUY rule as an example — when AI is confident AND risk is manageable.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 10 — INTERACTIVE DASHBOARD (dark)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.darkBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("10", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Interactive Streamlit Dashboard", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 26, bold: true, color: C.white, fontFace: "Calibri", align: "left", margin: 0
    });

    const pages = [
      {
        title: "🕯️ Live Market",
        desc: "Real-time candlestick charts with coin selector. Monitor prices and volume as they happen.",
        color: C.accent
      },
      {
        title: "📊 Historical Analysis",
        desc: "Deep-dive into technical indicators over time. Correlation heatmaps reveal hidden relationships.",
        color: C.accent2
      },
      {
        title: "🤖 Prediction & Risk",
        desc: "Probability gauges, feature importance bars, and interactive 3D risk cluster scatter plots.",
        color: C.gold
      },
      {
        title: "📈 Performance",
        desc: "Side-by-side RF vs LR comparison. Accuracy scores, confusion matrices, and ROC curves.",
        color: C.green
      },
    ];

    pages.forEach((page, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = 0.5 + col * 4.85;
      const y = 1.05 + row * 2.2;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y, w: 4.55, h: 2.0, fill: { color: C.cardBg }, rectRadius: 0.12,
        shadow: { type: "outer", color: "000000", blur: 10, offset: 3, angle: 45, opacity: 0.35 }
      });
      // Top color band
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 4.55, h: 0.55, fill: { color: page.color, transparency: 20 }, rectRadius: 0.12 });
      sl.addText(page.title, { x: x + 0.15, y: y + 0.08, w: 4.25, h: 0.4, fontSize: 14, bold: true, color: C.white, margin: 0, fontFace: "Calibri" });
      sl.addText(page.desc, { x: x + 0.15, y: y + 0.65, w: 4.25, h: 1.2, fontSize: 11.5, color: C.muted, margin: 0, fontFace: "Calibri" });
    });

    sl.addNotes("Speaker 3: Demo or walk through each page. Emphasize the user-friendly design — no ML knowledge needed to use it.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 11 — RESULTS & ACHIEVEMENTS (light)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.lightBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("11", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Results & Achievements", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 28, bold: true, color: C.textDark, fontFace: "Calibri", align: "left", margin: 0
    });

    // Big stat callouts
    const stats = [
      { val: ">80%", label: "Model Accuracy", sub: "on unseen test data", color: "0D9488" },
      { val: "100%", label: "API Uptime", sub: "via Binance ➡ Yahoo fallback", color: C.accent2 },
      { val: "3-in-1", label: "AI Fusion", sub: "Supervised + Unsupervised + Agent", color: "B45309" },
    ];

    stats.forEach((s, i) => {
      const x = 0.5 + i * 3.1;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y: 1.0, w: 2.9, h: 1.5, fill: { color: C.white }, rectRadius: 0.12,
        shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 45, opacity: 0.1 }
      });
      sl.addText(s.val, { x, y: 1.05, w: 2.9, h: 0.75, fontSize: 38, bold: true, color: s.color, align: "center", margin: 0, fontFace: "Calibri" });
      sl.addText(s.label, { x, y: 1.82, w: 2.9, h: 0.3, fontSize: 12, bold: true, color: C.textDark, align: "center", margin: 0, fontFace: "Calibri" });
      sl.addText(s.sub, { x, y: 2.15, w: 2.9, h: 0.27, fontSize: 9.5, color: C.mutedDim, align: "center", margin: 0, fontFace: "Calibri", italic: true });
    });

    // Achievement cards
    const achievements = [
      { icon: "⚙️", text: "Fully automated end-to-end data pipeline — from raw API data to trading recommendation." },
      { icon: "🔁", text: "Seamless API fallback ensures zero downtime even when Binance is unreachable." },
      { icon: "💡", text: "Intelligent Agent translates complex AI math into plain-English BUY/SELL/HOLD advice." },
      { icon: "📊", text: "Interactive dashboard makes the system accessible to non-technical retail investors." },
    ];

    achievements.forEach((a, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = 0.5 + col * 4.85;
      const y = 2.65 + row * 1.1;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y, w: 4.55, h: 0.9, fill: { color: C.white }, rectRadius: 0.1,
        shadow: { type: "outer", color: "000000", blur: 5, offset: 2, angle: 45, opacity: 0.08 }
      });
      sl.addText(a.icon, { x: x + 0.1, y: y + 0.15, w: 0.5, h: 0.5, fontSize: 20, align: "center", margin: 0, fontFace: "Calibri" });
      sl.addText(a.text, { x: x + 0.7, y: y + 0.08, w: 3.7, h: 0.75, fontSize: 11, color: C.textMid, valign: "middle", margin: 0, fontFace: "Calibri" });
    });

    sl.addNotes("All speakers: Whoever is most comfortable with numbers. Highlight the >80% accuracy and the seamless fallback robustness.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 12 — FUTURE ENHANCEMENTS (dark)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.darkBg };

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("12", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Future Enhancements", {
      x: 0.5, y: 0.25, w: 9, h: 0.55,
      fontSize: 28, bold: true, color: C.white, fontFace: "Calibri", align: "left", margin: 0
    });

    const enhancements = [
      {
        phase: "Near Term",
        icon: "🧠",
        title: "Deep Learning Models",
        desc: "Integrate LSTMs and Transformers for superior sequential pattern recognition in time-series price data.",
        color: C.accent
      },
      {
        phase: "Near Term",
        icon: "📰",
        title: "NLP Sentiment Analysis",
        desc: "Process real-time crypto news and Twitter feeds to enrich predictions with market sentiment signals.",
        color: C.accent2
      },
      {
        phase: "Mid Term",
        icon: "🔄",
        title: "Backtesting Engine",
        desc: "Simulate portfolio performance on historical data to validate strategy effectiveness before live deployment.",
        color: C.gold
      },
      {
        phase: "Mid Term",
        icon: "⚡",
        title: "WebSocket Streaming",
        desc: "Move from REST polling to WebSockets for millisecond-level tick data and sub-second dashboard updates.",
        color: C.green
      },
    ];

    enhancements.forEach((e, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = 0.5 + col * 4.85;
      const y = 1.1 + row * 2.1;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y, w: 4.55, h: 1.9, fill: { color: C.cardBg }, rectRadius: 0.12,
        shadow: { type: "outer", color: "000000", blur: 10, offset: 3, angle: 45, opacity: 0.35 }
      });
      // Phase badge
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: y + 0.14, w: 1.2, h: 0.3, fill: { color: e.color, transparency: 20 }, rectRadius: 0.06 });
      sl.addText(e.phase, { x: x + 0.15, y: y + 0.14, w: 1.2, h: 0.3, fontSize: 9, color: C.white, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });
      // Icon + title
      sl.addText(e.icon + "  " + e.title, { x: x + 0.15, y: y + 0.55, w: 4.2, h: 0.4, fontSize: 14, bold: true, color: e.color, margin: 0, fontFace: "Calibri" });
      sl.addText(e.desc, { x: x + 0.15, y: y + 1.0, w: 4.2, h: 0.8, fontSize: 11, color: C.muted, margin: 0, fontFace: "Calibri" });
    });

    sl.addNotes("Speaker 1 or 3: Show the roadmap beyond the FYP. LSTM and sentiment are the most impactful near-term additions.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 13 — CONCLUSION (dark, premium)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.darkBg };

    // Decorative circles
    sl.addShape(pres.shapes.OVAL, { x: 7.5, y: 0.5, w: 3.5, h: 3.5, fill: { color: C.accent2, transparency: 91 }, line: { color: C.accent2, width: 1, transparency: 80 } });
    sl.addShape(pres.shapes.OVAL, { x: 8.2, y: 1.2, w: 2.0, h: 2.0, fill: { color: C.accent, transparency: 93 }, line: { color: C.accent, width: 1, transparency: 70 } });
    sl.addShape(pres.shapes.OVAL, { x: -0.5, y: 3.5, w: 2.5, h: 2.5, fill: { color: C.accent, transparency: 90 } });

    sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fill: { color: C.accent2 }, rectRadius: 0.05 });
    sl.addText("13", { x: 9.3, y: 0.15, w: 0.5, h: 0.35, fontSize: 10, color: C.white, bold: true, align: "center", valign: "middle", margin: 0, fontFace: "Calibri" });

    sl.addText("Conclusion", {
      x: 0.5, y: 0.3, w: 9, h: 0.6,
      fontSize: 32, bold: true, color: C.white, fontFace: "Calibri", align: "left", margin: 0
    });

    const takeaways = [
      { icon: "🔗", text: "Built a complete, intelligent financial ecosystem — not just a prediction script." },
      { icon: "🧪", text: "Combined Supervised ML, Unsupervised Clustering, and Rule-Based Agents in one platform." },
      { icon: "💬", text: "Bridges the gap between complex AI algorithms and retail investor decision-making." },
    ];

    takeaways.forEach((t, i) => {
      const y = 1.15 + i * 1.0;
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 0.5, y, w: 8.8, h: 0.85, fill: { color: C.cardBg }, rectRadius: 0.1,
        shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 45, opacity: 0.3 }
      });
      sl.addText(t.icon, { x: 0.65, y: y + 0.15, w: 0.5, h: 0.5, fontSize: 22, align: "center", margin: 0, fontFace: "Calibri" });
      sl.addText(t.text, { x: 1.3, y: y + 0.1, w: 7.8, h: 0.65, fontSize: 13, color: C.offWhite, valign: "middle", margin: 0, fontFace: "Calibri" });
    });

    // Closing line
    sl.addShape(pres.shapes.LINE, { x: 0.5, y: 4.35, w: 9, h: 0, line: { color: C.mutedDim, width: 0.5 } });
    sl.addText("Thank you for your time and attention!", {
      x: 0.5, y: 4.5, w: 9.0, h: 0.5,
      fontSize: 14, color: C.muted, align: "center", italic: true, fontFace: "Calibri", margin: 0
    });

    sl.addNotes("Speaker 1: Wrap up by summarizing the three pillars. End with the impact statement about bridging AI and retail investors.");
  }

  // ─────────────────────────────────────────────────────────────
  // SLIDE 14 — Q&A (dark, minimal)
  // ─────────────────────────────────────────────────────────────
  {
    const sl = pres.addSlide();
    sl.background = { color: C.darkBg };

    // Large decorative question mark shape
    sl.addShape(pres.shapes.OVAL, { x: 3.0, y: 0.8, w: 4.0, h: 4.0, fill: { color: C.accent2, transparency: 92 }, line: { color: C.accent2, width: 1, transparency: 75 } });
    sl.addShape(pres.shapes.OVAL, { x: 3.5, y: 1.3, w: 3.0, h: 3.0, fill: { color: C.accent, transparency: 95 } });

    sl.addText("Q & A", {
      x: 1.0, y: 1.3, w: 8.0, h: 1.5,
      fontSize: 72, bold: true, color: C.white, align: "center", fontFace: "Calibri", margin: 0
    });

    sl.addText("Questions & Discussion", {
      x: 1.0, y: 3.0, w: 8.0, h: 0.5,
      fontSize: 18, color: C.accent, align: "center", fontFace: "Calibri", margin: 0, italic: true
    });

    sl.addShape(pres.shapes.LINE, { x: 2.5, y: 3.65, w: 5.0, h: 0, line: { color: C.mutedDim, width: 0.5 } });

    sl.addText("We are now open to any questions.", {
      x: 1.0, y: 3.75, w: 8.0, h: 0.4,
      fontSize: 13, color: C.muted, align: "center", fontFace: "Calibri", margin: 0
    });

    // Team names row
    sl.addText("[Member 1]  •  [Member 2]  •  [Member 3]", {
      x: 1.0, y: 4.3, w: 8.0, h: 0.35,
      fontSize: 12, color: C.mutedDim, align: "center", fontFace: "Calibri", margin: 0
    });

    sl.addNotes("All speakers: Stand together. Be prepared for questions about model choice, accuracy, limitations, and future work.");
  }

  await pres.writeFile({ fileName: "AI_Crypto_Analyzer_Presentation.pptx" });
  console.log("✅ Presentation saved successfully!");
}

buildPresentation().catch(console.error);
