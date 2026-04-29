"""
╔══════════════════════════════════════════════════════════════╗
║   Terzaghi Bearing Capacity Calculator — Shallow Foundation  ║
║   Run: python terzaghi_calculator.py                         ║
║   Requires: pip install pillow  (optional, for extra icons)  ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import csv
import io
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
#  COLOR PALETTE  — Engineering Blueprint Dark Theme
# ═══════════════════════════════════════════════════════════════
C = {
    "bg":          "#0F1923",   # deep navy background
    "panel":       "#162230",   # card panels
    "panel2":      "#1C2B3A",   # lighter card
    "border":      "#243447",   # border lines
    "accent":      "#00C2FF",   # electric blue accent
    "accent2":     "#00E5A0",   # emerald green
    "accent3":     "#FFB340",   # amber warning
    "text":        "#E8F4FD",   # primary text
    "text2":       "#7FA8C9",   # secondary text
    "text3":       "#3E6285",   # muted text
    "danger":      "#FF5A5A",   # red error
    "success":     "#00C87A",   # green ok
    "input_bg":    "#0D1B2A",   # input field bg
    "input_border":"#2A4A6B",   # input border
    "input_focus": "#00C2FF",   # focused input
    "row_even":    "#162230",
    "row_odd":     "#1C2B3A",
    "header_bg":   "#1A3A5C",
    "btn_calc":    "#0066CC",
    "btn_clear":   "#1C2B3A",
    "btn_export":  "#1A3A2A",
}

FONT_TITLE  = ("Courier New", 18, "bold")
FONT_HEAD   = ("Courier New", 11, "bold")
FONT_LABEL  = ("Courier New", 10)
FONT_INPUT  = ("Courier New", 11)
FONT_RESULT = ("Courier New", 24, "bold")
FONT_SMALL  = ("Courier New", 9)
FONT_TABLE  = ("Courier New", 10)
FONT_BTN    = ("Courier New", 11, "bold")


# ═══════════════════════════════════════════════════════════════
#  ENGINEERING CALCULATIONS
# ═══════════════════════════════════════════════════════════════
def terzaghi_factors(phi_deg):
    if phi_deg == 0:
        return 5.71, 1.0, 0.0
    phi = math.radians(phi_deg)
    Nq = math.exp(math.pi * math.tan(phi)) * math.tan(math.pi/4 + phi/2)**2
    Nc = (Nq - 1) / math.tan(phi)
    Ng = 2 * (Nq + 1) * math.tan(phi)
    return Nc, Nq, Ng


def calc(B, L, Df, c, phi, gamma, FS):
    Nc, Nq, Ng = terzaghi_factors(phi)
    ratio = B / L
    sc = sq = sg = None

    if ratio >= 0.95:
        ftype = "Square"
        q_ult = 1.3*c*Nc + gamma*Df*Nq + 0.4*gamma*B*Ng
    elif ratio < 0.15:
        ftype = "Strip"
        q_ult = c*Nc + gamma*Df*Nq + 0.5*gamma*B*Ng
    else:
        ftype = "Rectangular"
        sc = 1 + 0.2*(B/L)
        sq = 1 + 0.1*(B/L)
        sg = 1 - 0.1*(B/L)
        q_ult = c*Nc*sc + gamma*Df*Nq*sq + 0.5*gamma*B*Ng*sg

    q_all = q_ult / FS
    q0    = gamma * Df
    return dict(ftype=ftype, Nc=Nc, Nq=Nq, Ng=Ng,
                sc=sc, sq=sq, sg=sg, q0=q0,
                q_ult=q_ult, q_all=q_all)


# ═══════════════════════════════════════════════════════════════
#  STYLED WIDGET HELPERS
# ═══════════════════════════════════════════════════════════════
class StyledEntry(tk.Frame):
    """Input field with label, unit badge, and focus highlight."""
    def __init__(self, parent, label, unit="", default="", width=10, **kw):
        super().__init__(parent, bg=C["panel2"], **kw)
        tk.Label(self, text=label, font=FONT_LABEL, fg=C["text2"],
                 bg=C["panel2"], anchor="w").pack(fill="x", padx=2)

        row = tk.Frame(self, bg=C["panel2"])
        row.pack(fill="x")

        self.var = tk.StringVar(value=default)
        self.entry = tk.Entry(row, textvariable=self.var, width=width,
                              font=FONT_INPUT, bg=C["input_bg"],
                              fg=C["accent"], insertbackground=C["accent"],
                              relief="flat", bd=0,
                              highlightthickness=1,
                              highlightbackground=C["input_border"],
                              highlightcolor=C["input_focus"])
        self.entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 2))

        if unit:
            tk.Label(row, text=unit, font=FONT_SMALL, fg=C["text3"],
                     bg=C["input_bg"], padx=6).pack(side="left")

    def get(self):
        return self.var.get()


def section_label(parent, text):
    f = tk.Frame(parent, bg=C["bg"])
    f.pack(fill="x", pady=(14, 4))
    tk.Frame(f, height=1, bg=C["accent"]).pack(fill="x")
    row = tk.Frame(f, bg=C["bg"])
    row.pack(fill="x")
    tk.Label(row, text=f"  {text}  ", font=FONT_HEAD,
             fg=C["accent"], bg=C["bg"]).pack(side="left")
    tk.Frame(row, height=1, bg=C["border"]).pack(side="left", fill="x", expand=True, pady=6)
    return f


def metric_card(parent, label, value_var, unit="kPa", color=None):
    color = color or C["accent"]
    card = tk.Frame(parent, bg=C["panel"], bd=0,
                    highlightthickness=1, highlightbackground=C["border"])
    tk.Label(card, text=label, font=FONT_SMALL, fg=C["text2"],
             bg=C["panel"]).pack(pady=(10, 0), padx=12)
    val_lbl = tk.Label(card, textvariable=value_var, font=FONT_RESULT,
                       fg=color, bg=C["panel"])
    val_lbl.pack(padx=12)
    tk.Label(card, text=unit, font=FONT_SMALL, fg=C["text3"],
             bg=C["panel"]).pack(pady=(0, 10), padx=12)
    return card


# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
class TerzaghiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Terzaghi Bearing Capacity Calculator")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.geometry("880x820")
        self.minsize(820, 700)

        self._last_result = None
        self._build_ui()

    # ─── Build UI ───────────────────────────────────────────────
    def _build_ui(self):
        # ── Top banner ──
        banner = tk.Frame(self, bg=C["panel"], pady=0)
        banner.pack(fill="x")
        tk.Frame(banner, height=3, bg=C["accent"]).pack(fill="x")
        inner = tk.Frame(banner, bg=C["panel"])
        inner.pack(fill="x", padx=24, pady=12)
        tk.Label(inner, text="⬛ TERZAGHI BEARING CAPACITY",
                 font=FONT_TITLE, fg=C["accent"], bg=C["panel"]).pack(side="left")
        tk.Label(inner, text="Shallow Foundation  //  General Shear Failure",
                 font=FONT_SMALL, fg=C["text2"], bg=C["panel"]).pack(side="left", padx=16)
        self._clock_var = tk.StringVar()
        tk.Label(inner, textvariable=self._clock_var,
                 font=FONT_SMALL, fg=C["text3"], bg=C["panel"]).pack(side="right")
        self._tick()

        # ── Scrollable main body ──
        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=C["bg"])
        body_win = canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(body_win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        pad = dict(padx=28, pady=0)

        # ── Input section ──
        section_label(body, "▶  INPUT PARAMETERS").pack(fill="x", **pad)

        inp_outer = tk.Frame(body, bg=C["bg"])
        inp_outer.pack(fill="x", **pad)

        # Left col — Geometry
        geo_frame = tk.LabelFrame(inp_outer, text=" Foundation Geometry ",
                                  font=FONT_HEAD, fg=C["text2"],
                                  bg=C["panel2"], bd=0,
                                  highlightthickness=1, highlightbackground=C["border"],
                                  pady=10, padx=12)
        geo_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=4)

        fields_geo = [
            ("B  —  width",        "m",      "1.50", "B"),
            ("L  —  length",       "m",      "2.00", "L"),
            ("Df —  depth",        "m",      "1.00", "Df"),
            ("FS —  factor safety","",       "3.00", "FS"),
        ]
        self._entries = {}
        for i, (lbl, unit, default, key) in enumerate(fields_geo):
            e = StyledEntry(geo_frame, lbl, unit, default)
            e.grid(row=i, column=0, sticky="ew", pady=5)
            geo_frame.columnconfigure(0, weight=1)
            self._entries[key] = e

        # Right col — Soil
        soil_frame = tk.LabelFrame(inp_outer, text=" Soil Parameters ",
                                   font=FONT_HEAD, fg=C["text2"],
                                   bg=C["panel2"], bd=0,
                                   highlightthickness=1, highlightbackground=C["border"],
                                   pady=10, padx=12)
        soil_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=4)

        fields_soil = [
            ("c  —  cohesion",        "kPa",  "10.0", "c"),
            ("φ  —  friction angle",  "°",    "30.0", "phi"),
            ("γ  —  unit weight",     "kN/m³","18.0", "gamma"),
        ]
        for i, (lbl, unit, default, key) in enumerate(fields_soil):
            e = StyledEntry(soil_frame, lbl, unit, default)
            e.grid(row=i, column=0, sticky="ew", pady=5)
            soil_frame.columnconfigure(0, weight=1)
            self._entries[key] = e

        inp_outer.columnconfigure(0, weight=1)
        inp_outer.columnconfigure(1, weight=1)

        # ── Buttons ──
        btn_frame = tk.Frame(body, bg=C["bg"])
        btn_frame.pack(fill="x", **pad, pady=12)

        tk.Button(btn_frame, text="  ⚡  CALCULATE  ",
                  font=FONT_BTN, fg="white", bg=C["btn_calc"],
                  activebackground="#0055AA", activeforeground="white",
                  relief="flat", cursor="hand2", bd=0,
                  padx=20, pady=10,
                  command=self._calculate).pack(side="left", padx=(0, 10))

        tk.Button(btn_frame, text="  ✕  CLEAR  ",
                  font=FONT_BTN, fg=C["text2"], bg=C["btn_clear"],
                  activebackground=C["border"], activeforeground=C["text"],
                  relief="flat", cursor="hand2", bd=0,
                  padx=20, pady=10,
                  command=self._clear).pack(side="left", padx=(0, 10))

        tk.Button(btn_frame, text="  ↓  EXPORT CSV  ",
                  font=FONT_BTN, fg=C["accent2"], bg=C["btn_export"],
                  activebackground="#0D2A1A", activeforeground=C["accent2"],
                  relief="flat", cursor="hand2", bd=0,
                  padx=20, pady=10,
                  command=self._export).pack(side="left")

        # ── Result metric cards ──
        section_label(body, "▶  RESULTS").pack(fill="x", **pad)

        cards_frame = tk.Frame(body, bg=C["bg"])
        cards_frame.pack(fill="x", **pad, pady=4)

        self._qult_var = tk.StringVar(value="—")
        self._qall_var = tk.StringVar(value="—")
        self._fs_var   = tk.StringVar(value="—")

        mc1 = metric_card(cards_frame, "q_ult  (Ultimate Bearing Capacity)",
                          self._qult_var, "kPa", C["accent"])
        mc1.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        mc2 = metric_card(cards_frame, "q_all  (Allowable Bearing Capacity)",
                          self._qall_var, "kPa", C["accent2"])
        mc2.grid(row=0, column=1, sticky="ew", padx=(6, 6))

        mc3 = metric_card(cards_frame, "Factor of Safety (FS)",
                          self._fs_var,   "", C["accent3"])
        mc3.grid(row=0, column=2, sticky="ew", padx=(6, 0))

        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)

        # ── Status bar ──
        self._status_var = tk.StringVar(value="Ready.")
        self._status_color = tk.StringVar(value=C["text3"])
        status_bar = tk.Frame(body, bg=C["panel"], pady=4)
        status_bar.pack(fill="x", **pad, pady=(6, 0))
        self._status_lbl = tk.Label(status_bar, textvariable=self._status_var,
                                    font=FONT_SMALL, fg=C["text3"], bg=C["panel"],
                                    anchor="w", padx=10)
        self._status_lbl.pack(fill="x")

        # ── Detailed results table ──
        section_label(body, "▶  DETAILED CALCULATION TABLE").pack(fill="x", **pad)

        tbl_outer = tk.Frame(body, bg=C["panel"],
                             highlightthickness=1, highlightbackground=C["border"])
        tbl_outer.pack(fill="x", **pad, pady=(0, 12))

        cols = ("Parameter", "Symbol", "Value", "Unit", "Note")
        self._tree = ttk.Treeview(tbl_outer, columns=cols,
                                  show="headings", height=18)
        self._style_table()

        for col in cols:
            anchor = "center" if col != "Parameter" else "w"
            self._tree.heading(col, text=col)
            w = {"Parameter": 240, "Symbol": 90, "Value": 120,
                 "Unit": 80, "Note": 220}[col]
            self._tree.column(col, width=w, anchor=anchor, stretch=True)

        vsb = ttk.Scrollbar(tbl_outer, orient="vertical",
                            command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        # ── Formula reference ──
        section_label(body, "▶  FORMULA REFERENCE").pack(fill="x", **pad)
        formula_txt = (
            "Strip:       q_ult = c·Nc + γ·Df·Nq + 0.5·γ·B·Nγ\n"
            "Square:      q_ult = 1.3·c·Nc + γ·Df·Nq + 0.4·γ·B·Nγ\n"
            "Rectangular: q_ult = c·Nc·sc + γ·Df·Nq·sq + 0.5·γ·B·Nγ·sγ\n\n"
            "Nq = exp(π·tanφ)·tan²(45+φ/2)     Nc = (Nq−1)/tanφ     Nγ = 2(Nq+1)·tanφ\n"
            "Shape factors (rect): sc=1+0.2B/L   sq=1+0.1B/L   sγ=1−0.1B/L\n"
            "q_all = q_ult / FS"
        )
        fbox = tk.Frame(body, bg=C["panel2"],
                        highlightthickness=1, highlightbackground=C["border"])
        fbox.pack(fill="x", **pad, pady=(0, 20))
        tk.Label(fbox, text=formula_txt, font=FONT_SMALL,
                 fg=C["text2"], bg=C["panel2"],
                 justify="left", padx=16, pady=12).pack(fill="x")

    # ─── Style table ────────────────────────────────────────────
    def _style_table(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
                        background=C["row_even"],
                        fieldbackground=C["row_even"],
                        foreground=C["text"],
                        rowheight=26,
                        font=FONT_TABLE,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=C["header_bg"],
                        foreground=C["accent"],
                        font=("Courier New", 10, "bold"),
                        borderwidth=0, relief="flat")
        style.map("Treeview",
                  background=[("selected", C["accent"])],
                  foreground=[("selected", C["bg"])])
        self._tree.tag_configure("odd",    background=C["row_odd"])
        self._tree.tag_configure("even",   background=C["row_even"])
        self._tree.tag_configure("result", background="#0D2238",
                                 foreground=C["accent"])
        self._tree.tag_configure("qult",   background="#0D1E38",
                                 foreground=C["accent"])
        self._tree.tag_configure("qall",   background="#0D2218",
                                 foreground=C["accent2"])
        self._tree.tag_configure("factor", background="#1A2010",
                                 foreground=C["accent3"])

    # ─── Tick clock ─────────────────────────────────────────────
    def _tick(self):
        self._clock_var.set(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.after(1000, self._tick)

    # ─── Get & validate inputs ───────────────────────────────────
    def _get_inputs(self):
        vals = {}
        for key, entry in self._entries.items():
            raw = entry.get().strip()
            try:
                vals[key] = float(raw)
            except ValueError:
                raise ValueError(f"Invalid value for '{key}': '{raw}'")
        return vals

    def _validate(self, v):
        errors = []
        if v["B"] <= 0 or v["L"] <= 0 or v["Df"] <= 0:
            errors.append("B, L, Df must be > 0")
        if v["FS"] < 1:
            errors.append("FS must be ≥ 1")
        if not (0 <= v["phi"] <= 45):
            errors.append("φ must be 0 – 45°")
        if v["gamma"] <= 0:
            errors.append("γ must be > 0")
        if v["c"] < 0:
            errors.append("c must be ≥ 0")
        return errors

    # ─── Calculate ───────────────────────────────────────────────
    def _calculate(self):
        try:
            v = self._get_inputs()
        except ValueError as e:
            self._set_status(str(e), "error")
            return

        errs = self._validate(v)
        if errs:
            self._set_status("  ⚠  " + "  |  ".join(errs), "error")
            return

        r = calc(v["B"], v["L"], v["Df"], v["c"], v["phi"], v["gamma"], v["FS"])
        self._last_result = {**v, **r}

        # Metric cards
        self._qult_var.set(f"{r['q_ult']:.2f}")
        self._qall_var.set(f"{r['q_all']:.2f}")
        self._fs_var.set(f"{v['FS']:.1f}")

        # Status
        self._set_status(
            f"  ✔  [{r['ftype']} footing]  "
            f"q_ult = {r['q_ult']:.2f} kPa  |  "
            f"q_all = {r['q_all']:.2f} kPa  |  "
            f"Nc={r['Nc']:.3f}  Nq={r['Nq']:.3f}  Nγ={r['Ng']:.3f}",
            "ok"
        )

        self._fill_table(v, r)

    # ─── Fill detailed table ─────────────────────────────────────
    def _fill_table(self, v, r):
        for row in self._tree.get_children():
            self._tree.delete(row)

        rows = [
            # Label, Symbol, Value, Unit, Note, tag
            ("── INPUT ──",              "",      "",                   "",        "",                          "factor"),
            ("Width",                    "B",     f"{v['B']:.3f}",      "m",       "Foundation width",          "even"),
            ("Length",                   "L",     f"{v['L']:.3f}",      "m",       "Foundation length",         "odd"),
            ("Depth of foundation",      "Df",    f"{v['Df']:.3f}",     "m",       "Embedment depth",           "even"),
            ("Cohesion",                 "c",     f"{v['c']:.3f}",      "kPa",     "Soil cohesion",             "odd"),
            ("Friction angle",           "φ",     f"{v['phi']:.3f}",    "°",       "Internal friction angle",   "even"),
            ("Unit weight",              "γ",     f"{v['gamma']:.3f}",  "kN/m³",   "Bulk unit weight",          "odd"),
            ("Factor of safety",         "FS",    f"{v['FS']:.2f}",     "—",       "Applied to q_ult",          "even"),
            ("B / L ratio",              "B/L",   f"{v['B']/v['L']:.4f}", "—",    "Foundation shape indicator","odd"),
            ("Foundation type",          "—",     r['ftype'],           "—",       "Auto-detected",             "even"),
            ("── BEARING FACTORS ──",    "",      "",                   "",        "Terzaghi (1943)",           "factor"),
            ("Bearing factor Nc",        "Nc",    f"{r['Nc']:.4f}",     "—",       "Cohesion factor",           "even"),
            ("Bearing factor Nq",        "Nq",    f"{r['Nq']:.4f}",     "—",       "Surcharge factor",          "odd"),
            ("Bearing factor Nγ",        "Nγ",    f"{r['Ng']:.4f}",     "—",       "Self-weight factor",        "even"),
        ]

        if r["sc"] is not None:
            rows += [
                ("── SHAPE FACTORS ──",  "",      "",                   "",        "Rectangular footing",       "factor"),
                ("Shape factor sc",      "sc",    f"{r['sc']:.4f}",     "—",       "sc = 1 + 0.2(B/L)",         "even"),
                ("Shape factor sq",      "sq",    f"{r['sq']:.4f}",     "—",       "sq = 1 + 0.1(B/L)",         "odd"),
                ("Shape factor sγ",      "sγ",    f"{r['sg']:.4f}",     "—",       "sγ = 1 − 0.1(B/L)",         "even"),
            ]

        rows += [
            ("── STRESS TERMS ──",       "",      "",                   "",        "",                          "factor"),
            ("Overburden pressure",      "q₀",    f"{r['q0']:.3f}",     "kPa",     "γ × Df",                    "even"),
            ("Cohesion term c·Nc",       "cNc",   f"{v['c']*r['Nc']:.3f}", "kPa",  "Cohesion contribution",     "odd"),
            ("Surcharge term γDfNq",     "qNq",   f"{r['q0']*r['Nq']:.3f}", "kPa", "Surcharge contribution",    "even"),
            ("Self-wt term 0.5γBNγ",     "0.5γBNγ",f"{0.5*v['gamma']*v['B']*r['Ng']:.3f}","kPa","Self-weight contribution","odd"),
            ("── RESULT ──",             "",      "",                   "",        "",                          "factor"),
            ("Ultimate bearing capacity","q_ult",  f"{r['q_ult']:.4f}", "kPa",     "q_all × FS",                "qult"),
            ("Allowable bearing capacity","q_all", f"{r['q_all']:.4f}", "kPa",     "q_ult / FS",                "qall"),
        ]

        for data in rows:
            lbl, sym, val, unit, note, tag = data
            self._tree.insert("", "end",
                              values=(lbl, sym, val, unit, note),
                              tags=(tag,))

    # ─── Status bar ─────────────────────────────────────────────
    def _set_status(self, msg, kind="ok"):
        color = {"ok": C["success"], "error": C["danger"],
                 "info": C["text3"]}.get(kind, C["text3"])
        self._status_var.set(msg)
        self._status_lbl.configure(fg=color)

    # ─── Clear ───────────────────────────────────────────────────
    def _clear(self):
        defaults = {"B":"1.50","L":"2.00","Df":"1.00","FS":"3.00",
                    "c":"10.0","phi":"30.0","gamma":"18.0"}
        for key, entry in self._entries.items():
            entry.var.set(defaults.get(key, ""))
        self._qult_var.set("—")
        self._qall_var.set("—")
        self._fs_var.set("—")
        for row in self._tree.get_children():
            self._tree.delete(row)
        self._last_result = None
        self._set_status("Ready.", "info")

    # ─── Export CSV ──────────────────────────────────────────────
    def _export(self):
        if not self._last_result:
            messagebox.showwarning("No Data", "Please calculate first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"terzaghi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not path:
            return
        r = self._last_result
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Terzaghi Bearing Capacity — Export",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            w.writerow([])
            w.writerow(["Parameter", "Symbol", "Value", "Unit"])
            rows_export = [
                ("Width",                    "B",      r['B'],        "m"),
                ("Length",                   "L",      r['L'],        "m"),
                ("Depth",                    "Df",     r['Df'],       "m"),
                ("Cohesion",                 "c",      r['c'],        "kPa"),
                ("Friction angle",           "phi",    r['phi'],      "deg"),
                ("Unit weight",              "gamma",  r['gamma'],    "kN/m3"),
                ("Factor of safety",         "FS",     r['FS'],       "—"),
                ("Foundation type",          "type",   r['ftype'],    "—"),
                ("Nc",                       "Nc",     r['Nc'],       "—"),
                ("Nq",                       "Nq",     r['Nq'],       "—"),
                ("Ngamma",                   "Ng",     r['Ng'],       "—"),
                ("q_ult",                    "q_ult",  r['q_ult'],    "kPa"),
                ("q_all",                    "q_all",  r['q_all'],    "kPa"),
            ]
            for row in rows_export:
                w.writerow(row)
        self._set_status(f"  ✔  Exported → {path}", "ok")
        messagebox.showinfo("Export OK", f"Saved to:\n{path}")


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = TerzaghiApp()
    app.mainloop()
