import json
import re
import os

def generate_interactive_dashboard():
    log_filename = "simulation_log.txt"
    output_html = "../index.html"
    parsed_records = []

    print("Parsing simulation data stream for fully distinct UI layout...")
    
    if not os.path.exists(log_filename):
        print(f"Error: Could not find {log_filename} in this folder.")
        return

    with open(log_filename, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            cleaned_line = line.strip()
            if "{" in cleaned_line and "}" in cleaned_line:
                try:
                    start_idx = cleaned_line.index("{")
                    end_idx = cleaned_line.rindex("}") + 1
                    json_str = cleaned_line[start_idx:end_idx]
                    json_str = re.sub(r'(:\s*)(\d)\s+(\d)', r'\1"\2\3"', json_str)
                    record_json = json.loads(json_str)
                    parsed_records.append(record_json)
                except Exception as e:
                    continue

    js_data_array = []
    for record in parsed_records:
        hh = str(record.get("hour", "00")).strip()
        mm = str(record.get("minute", "00")).strip()
        ss = str(record.get("second", "00")).strip()
        time_val = record.get("time_ns", "0")
        is_triggered = 1 if int(record.get("alarm", 0)) == 1 else 0
        js_data_array.append(f"{{ ns: {time_val}, hh: '{hh}', mm: '{mm}', ss: '{ss}', alarm: {is_triggered} }}")
    
    js_array_string = ",\n        ".join(js_data_array)
    num_records = len(parsed_records)
    slider_max = num_records - 1 if num_records > 0 else 0

    # NEW: Completely re-engineered distinct layout with original shapes and colors
    html_layout = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>VLSI Digital Clock Dashboard</title>
    <style>
        body {{
            background-color: #0d0e12;
            color: #d1d5db;
            font-family: 'Segoe UI', system-ui, sans-serif;
            margin: 0;
            padding: 40px;
        }}
        .header-panel {{
            border-bottom: 2px dashed #374151;
            padding-bottom: 25px;
            margin-bottom: 40px;
        }}
        .header-panel h1 {{
            color: #f1f5f9;
            font-size: 30px;
            margin: 0;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        .header-panel p {{
            color: #f43f5e;
            margin: 5px 0 0 0;
            font-size: 13px;
            font-family: monospace;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }}
        .dashboard-layout {{
            display: flex;
            flex-direction: column;
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        /* NEW structural block: Side-by-side technical panels instead of uniform grid boxes */
        .main-hardware-row {{
            display: grid;
            grid-template-columns: 1.8fr 1.2fr;
            gap: 30px;
        }}
        .tech-panel {{
            background: #161b26;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 30px;
            position: relative;
        }}
        .tech-panel::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 3px;
            background: #f43f5e;
            border-radius: 8px 8px 0 0;
        }}
        .panel-heading {{
            font-family: monospace;
            font-size: 12px;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        /* Split view inside the main time panel */
        .time-split-view {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
        }}
        .time-block {{
            text-align: center;
        }}
        .large-digital-digits {{
            font-family: monospace;
            font-size: 64px;
            color: #f8fafc;
            font-weight: bold;
        }}
        .block-label {{
            font-size: 11px;
            color: #6b7280;
            text-transform: uppercase;
            margin-top: 5px;
        }}
        .divider-dots {{
            font-size: 48px;
            color: #374151;
            font-weight: bold;
            animation: blinker 1.5s linear infinite;
        }}
        @keyframes blinker {{ 50% {{ opacity: 0.3; }} }}

        /* Dedicated original alert module box */
        .alarm-status-container {{
            background: #1f293d;
            border-left: 4px solid #4b5563;
            padding: 20px;
            border-radius: 6px;
            min-width: 220px;
            text-align: center;
        }}
        .alarm-value-txt {{
            font-size: 24px;
            font-weight: bold;
            font-family: monospace;
            color: #e2e8f0;
            margin-bottom: 8px;
        }}
        .status-badge-pill {{
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
            padding: 5px 12px;
            border-radius: 4px;
            display: inline-block;
        }}
        .state-armed {{ background-color: #10b981; color: #fff; }}
        .state-alert {{ background-color: #ef4444; color: #fff; box-shadow: 0 0 15px rgba(239,68,68,0.3); }}

        /* Distinct layout lines for hardware metrics */
        .metrics-grid {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .metric-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px dashed #2d3748;
        }}
        .metric-name {{ font-size: 14px; color: #9ca3af; }}
        .metric-score {{ font-family: monospace; font-size: 14px; color: #f1f5f9; }}
        
        /* Control bar design */
        .interaction-panel {{
            background: #161b26;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 25px;
        }}
        .control-row-layout {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 30px;
        }}
        .nav-button {{
            background: transparent;
            border: 1px solid #f43f5e;
            color: #f43f5e;
            padding: 10px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-family: monospace;
            font-weight: bold;
            transition: all 0.2s;
        }}
        .nav-button:hover {{
            background: #f43f5e;
            color: #0d0e12;
        }}
        .slider-flex-wrapper {{
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .timeline-slider {{
            -webkit-appearance: none;
            width: 100%;
            height: 4px;
            background: #2d3748;
            outline: none;
            border-radius: 2px;
        }}
        .timeline-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 14px;
            height: 14px;
            background: #f43f5e;
            border-radius: 2px;
            cursor: pointer;
        }}
    </style>
</head>
<body>

    <div class="header-panel">
        <h1>VLSI-Based Digital Clock with Alarm Functionality</h1>
        <p>RTL Behavioral Verification & Synthesis Optimization Dashboard</p>
    </div>

    <div class="dashboard-layout">
        
        <div class="main-hardware-row">
            
            <!-- PANEL 1: CORE TIME CONTEXT RUNNER -->
            <div class="tech-panel">
                <div class="panel-heading">💾 Core Register State Memory</div>
                <div class="time-split-view">
                    
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div class="time-block">
                            <div id="lbl_hh" class="large-digital-digits">00</div>
                            <div class="block-label">Hours</div>
                        </div>
                        <div class="divider-dots">:</div>
                        <div class="time-block">
                            <div id="lbl_mm" class="large-digital-digits">00</div>
                            <div class="block-label">Minutes</div>
                        </div>
                        <div class="divider-dots">:</div>
                        <div class="time-block">
                            <div id="lbl_ss" class="large-digital-digits">00</div>
                            <div class="block-label">Seconds</div>
                        </div>
                    </div>

                    <div class="alarm-status-container">
                        <div class="block-label" style="margin-bottom: 5px;">Comparator Target</div>
                        <div class="alarm-value-txt">00 : 01</div>
                        <div id="badge_alarm" class="status-badge-pill state-armed">Armed</div>
                    </div>

                </div>
            </div>

            <!-- PANEL 2: HARDWARE SCHEMATIC SIZES -->
            <div class="tech-panel">
                <div class="panel-heading">📊 Synthesis Hardware Estimation</div>
                <div class="metrics-grid">
                    <div class="metric-item"><span class="metric-name">Slice LUT Units</span><span class="metric-score">56 / 20,800 (0.27%)</span></div>
                    <div class="metric-item"><span class="metric-name">Registers / Flip-Flops</span><span class="metric-score">44 / 41,600 (0.11%)</span></div>
                    <div class="metric-item"><span class="metric-name">DSP Multipliers</span><span class="metric-score">0 / 90 (0.00%)</span></div>
                    <div class="metric-item"><span class="metric-name">Block RAM Elements</span><span class="metric-score">0 / 50 (0.00%)</span></div>
                </div>
            </div>

        </div>

        <!-- PANEL 3: TIMELINE TRACKER CONTROL PANEL -->
        <div class="interaction-panel">
            <div class="panel-heading" style="margin-bottom:15px;">🕹️ Waveform Execution Step Trace</div>
            <div class="control-row-layout">
                <button class="nav-button" onclick="stepPrev()">[ PREV STEP ]</button>
                
                <div class="slider-flex-wrapper">
                    <div style="display:flex; justify-content:space-between; font-size:11px; font-family:monospace; color:#9ca3af;">
                        <span>T: 40,000 ns</span>
                        <span id="frame_lbl" style="color:#f43f5e;">Vector: 1 / 63</span>
                        <span>T: 5,010,000 ns</span>
                    </div>
                    <input type="range" min="0" max="{slider_max}" value="0" class="timeline-slider" id="time_slider" oninput="updateState(this.value)">
                </div>
                
                <button class="nav-button" onclick="stepNext()">[ NEXT STEP ]</button>
            </div>
            <div style="margin-top:15px; text-align:center; font-family:monospace; font-size:12px; color:#6b7280;" id="timestamp_lbl">
                SystemVerilog Trace Event: 40000 ns
            </div>
        </div>

    </div>

    <script>
        const simData = [
            {js_array_string}
        ];

        function updateState(index) {{
            const state = simData[index];
            
            document.getElementById("lbl_hh").innerText = state.hh;
            document.getElementById("lbl_mm").innerText = state.mm;
            document.getElementById("lbl_ss").innerText = state.ss;
            
            const alarmBadge = document.getElementById("badge_alarm");
            if (state.alarm === 1) {{
                alarmBadge.innerText = "🚨 CRITICAL ALERT";
                alarmBadge.className = "status-badge-pill state-alert";
            }} else {{
                alarmBadge.innerText = "🟢 SYSTEM ARMED";
                alarmBadge.className = "status-badge-pill state-armed";
            }}
            
            document.getElementById("frame_lbl").innerText = "Vector: " + (parseInt(index) + 1) + " / " + simData.length;
            document.getElementById("timestamp_lbl").innerText = "SystemVerilog Trace Event: " + state.ns + " ns";
            document.getElementById("time_slider").value = index;
        }}

        function stepNext() {{
            let currentVal = parseInt(document.getElementById("time_slider").value);
            if (currentVal < simData.length - 1) {{
                updateState(currentVal + 1);
            }}
        }}

        function stepPrev() {{
            let currentVal = parseInt(document.getElementById("time_slider").value);
            if (currentVal > 0) {{
                updateState(currentVal - 1);
            }}
        }}

        updateState(0);
    </script>

</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as out_file:
        out_file.write(html_layout)
    
    print("Success! Completely distinct Cyberpunk-styled interactive layout generated.")

if __name__ == "__main__":
    generate_interactive_dashboard()