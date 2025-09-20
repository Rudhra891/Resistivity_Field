import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import matplotlib.pyplot as plt
import xlsxwriter

st.set_page_config(page_title="RESISTIVITY DATA VIEWER", layout="wide")

# --- CSS for gradient background and nicer layout ---
st.markdown(
    """
    <style>
    .stApp {
      background: background-size: 100% 100%;
      background-position: 0px 0px;
      background-image: linear-gradient(90deg, #A044D6FF 0%, #71C4FFFF 100%);
      color: white;
    }
    .big-title {
      font-size:40px;
      font-weight:700;
      text-align:center;
      padding: 20px 0;
    }
    .card {background: rgba(255,255,255,0.06); padding: 12px; border-radius:10px}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">RESISTIVITY DATA VIEWER</div>', unsafe_allow_html=True)

# Initialize session state
if "lines" not in st.session_state:
    st.session_state.lines = {}  # Profiling lines
if "sounding" not in st.session_state:
    st.session_state.sounding = {}  # Sounding data

# --- Load geometric factor tables ---
@st.cache_data
def load_geometric_table():
    tables = {}
    try:
        tables[400] = pd.read_excel("geom_400.xlsx")
        tables[300] = pd.read_excel("geom_300.xlsx")
        tables["sounding"] = pd.read_excel("sound_geom.xlsx")
    except Exception as e:
        st.warning(f"Could not load geometric factor files: {e}")
    return tables

GEOM_TABLES = load_geometric_table()

def get_geometric_factor(mode, C1C2, line_number=None, station=None, P1P2=None):
    if mode == "Profiling":
        if int(C1C2) not in GEOM_TABLES:
            return 1.0
        df = GEOM_TABLES[int(C1C2)]
        match = df[(df["Line"] == line_number) & (df["Station"] == station)]
        if not match.empty:
            return float(match["GeometricFactor"].values[0])
        else:
            return 1.0
            
    
    
    elif mode == "Sounding":
        if "sounding" in GEOM_TABLES:                 # First, try to get the factor from the table
            df = GEOM_TABLES["sounding"]
            match = df[(df["C1C2"] == C1C2) & (df["P1P2"] == P1P2)]
            if not match.empty:
                return float(match["GeometricFactor"].values[0])
        # If we reach here, table doesn't have the factor or table missing
        # Use the custom formula instead of default 1.0
        try:
            # Note: C1C2 and P1P2 expected as floats
            # your formula: 3.1428 * ( ((C1C2/2)^2 - (P1P2)^2) / (2 * P1P2) )
            # In Python '^' is bitwise XOR; for power use '**'
            geom = 3.1428 * ( ((C1C2_val) ** 2 - (P1P2_val) ** 2) / (2 * P1P2_val) )
            return float(geom)
        except Exception as e:
            # If formula fails (e.g. P1P2 is zero or None), fallback to 1.0
            return 1.0
    else:
        return 1.0

    '''
    elif mode == "Sounding":
        if "sounding" not in GEOM_TABLES:
            return 1.0
        df = GEOM_TABLES["sounding"]
        match = df[(df["C1C2"] == C1C2) & (df["P1P2"] == P1P2)]
        if not match.empty:
            return float(match["GeometricFactor"].values[0])
        else:
            return 1.0
    else:
        return 1.0
    '''



# Sidebar/left panel for survey setup
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    mode = st.radio("Choose mode", ["Profiling", "Sounding"])
    st.markdown("</div>", unsafe_allow_html=True)

with col1:
    st.markdown('<div class="card" style="margin-top:12px">', unsafe_allow_html=True)
    st.subheader("Survey Info")
    date = st.date_input("Survey date", value=datetime.today()).strftime("%d-%m-%Y")
    client = st.text_input("Client name")
    loc_name = st.text_input("Location Name")
    #lat = st.number_input("Latitude",value=0.0,step=0.0001,format="%.4f")
    lat = st.text_input("Latitude",placeholder="17.24586")
    try:
        lat = float(lat)
        lat = round(lat,6)
    except:
        lat = None
        
    #long = st.number_input("Longitude",value=0.0,step=0.0001,format="%.4f")
    long = st.text_input("Longitude",placeholder="79.25487")
    try:
        long = float(long)
        long = round(long,6)
    except:
        long = None
    
    #geology = st.text_input("Geology")
    
    geology_options= ["Granitic","Granitoid gneiss","gneiss","charnockite", "khondalite","Basaltic","Limestone","Laterite","Quartzite",
                       "Migmatite","Shale","Schist","Dolerite","Anorthosite / gabbro / dunite","Porphyritic granite","Metabasite","Migmatitic","Alluvial-covered basement"
                      ]
    geology = st.selectbox("Geology",
                            options=geology_options + ["Other"]                    
    )
    if geology == "Other":
        geology_manual = st.text_input("Geology")
        if geology_manual:
            geology = geology_manual
    
    
    #soiltype = st.text_input("Soil type/Color")
    soil_options= ["Black Cotton Soil","Red Soil","Brown soil(dark)","Brown Soil (light)","Laterite soil","Clay"]
    soiltype = st.selectbox("Soil type/Color",
                            options=soil_options + ["Other"]                    
    )
    if soiltype == "Other":
        soiltype_manual = st.text_input("Soil Type/Color: ")
        if soiltype_manual:
            soiltype = soiltype_manual
    
    
    linedir = st.text_input("Line direction",placeholder="NS or EW or NE-SW or NW-SE")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PROFILING WORKFLOW ---
if mode == "Profiling":
    with col1:
        st.markdown('<div class="card" style="margin-top:12px">', unsafe_allow_html=True)
        prof_type = st.selectbox("Method", ["Gradient", "Wenner"])
        C1C2 = st.number_input("Enter C1C2 distance (e.g. 300 or 400)", min_value=1.0, value=400.0, step=100.0)
        P1P2 = st.number_input("Enter P1P2 interval (e.g. 5)", min_value=1.0, value=10.0, step=1.0)

        st.subheader("Line Setup")
        line_number = st.text_input("Line number",placeholder="L0/N50/S50/E50/W50/NE50/SW50/SE50/NW50")
        
        
        station = st.number_input("Station",value= None,placeholder="35/-35", step=5)
        #resistance = st.number_input("Resistance (ohms)", value=0.0,format="%.5f")
        resistance = st.text_input("Resistance (ohms)")
        try:
            resistance = float(resistance)
            resistance = round(resistance,6)
        except:
            resistance = None
        r_mark = st.text_input("Remark")

        if st.button("Record Profiling Data"):
            if not line_number:
                st.error("Please enter a line number.")
            else:
                if line_number not in st.session_state.lines:
                    st.session_state.lines[line_number] = {
                        "meta": {
                            "Date": str(date),
                            "Client": client,
                            "Location": loc_name,
                            "Latitude": lat,
                            "Longitude": long,
                            "Geology": geology,
                            "Soil Type/Color": soiltype,
                            "Line direction": linedir,
                            "Method": prof_type,
                            "C1C2": C1C2,
                            "P1P2": P1P2,
                        },
                        "data": {},
                    }
                gfactor = get_geometric_factor("Profiling", C1C2, line_number, station)
                #resistivity = round(resistance * gfactor, 6)
                
                if resistance is None:
                    st.error("⚠️ Please enter a proper resistance value.")
                    resistivity = None
 
                elif gfactor is None:
                    st.error("⚠️ Please enter a proper gfactor value.")
                    resistivity = None
                    
                else:
                    resistivity = round(resistance * gfactor, 6)
                        
           
                
                
                st.session_state.lines[line_number]["data"][station] = {
                    "station": station,
                    "resistance": resistance,
                    "gfactor": gfactor,
                    "resistivity": resistivity,
                    "remarks": r_mark,
                }
                st.success(f"Recorded/Updated station {station} in line {line_number}")
        st.markdown("</div>", unsafe_allow_html=True)

# --- SOUNDING WORKFLOW ---
if mode == "Sounding":
    with col1:
        st.markdown('<div class="card" style="margin-top:12px">', unsafe_allow_html=True)
        prof_type = st.selectbox("Method", ["Schlumberger", "Other"])
        
        #C1C2_val = st.number_input("Enter C1C2 (AB spacing)", min_value=1.0, value=10.0, step=1.0)
        C1C2_val = st.text_input("Enter C1C2/2 (AB/2)")
        try:
            C1C2_val = float(C1C2_val)
            C1C2_val = round(C1C2_val,6)
        except:
            C1C2_val = None
        
        
        #P1P2_val = st.number_input("Enter P1P2 (MN spacing)", min_value=1.0, value=1.0, step=1.0)
        
        P1P2_val = st.text_input("Enter P1P2/2 (MN/2)")
        try:
            P1P2_val = float(P1P2_val)
            P1P2_val = round(P1P2_val,6)
        except:
            P1P2_val = None
        
        
        #resistance = st.number_input("Resistance (ohms)", value=0.0, step=0.00001,format="%.5f")
        resistance = st.text_input("Resistance (ohms)")
        try:
            resistance = float(resistance)
            resistance = round(resistance,6)
        except:
            resistance = None
        r_mark = st.text_input("Remark")
        if st.button("Record Sounding Data"):
            gfactor = get_geometric_factor("Sounding", C1C2_val, P1P2=P1P2_val)
            #resistivity = round(resistance * gfactor, 6)
            
            if resistance is None:
                st.error("⚠️ Please enter a proper resistance value.")
                resistivity = None
 
            elif gfactor is None:
                st.error("⚠️ Please enter a proper gfactor value.")
                resistivity = None
                    
            else:
                resistivity = round(resistance * gfactor, 6)
            
            
            
            st.session_state.sounding[(C1C2_val, P1P2_val)] = {
                "C1C2/2": C1C2_val,
                "P1P2/2": P1P2_val,
                "resistance": resistance,
                "gfactor": gfactor,
                "resistivity": resistivity,
                "remark":r_mark
            }
            st.success(f"Recorded Sounding: C1C2/2={C1C2_val}, P1P2/2={P1P2_val}")
        st.markdown("</div>", unsafe_allow_html=True)

# Right panel: view/edit data
with col2:
    st.subheader("Data Viewer")
    if mode == "Profiling":
        if st.session_state.lines:
            selected_line = st.selectbox("Select line to view", list(st.session_state.lines.keys()))
            line_data = st.session_state.lines[selected_line]
            df = pd.DataFrame(line_data["data"].values())
            st.write("Meta:")
            st.json(line_data["meta"])
            st.write("Recorded Data:")
            st.dataframe(df)

            if not df.empty:
                fig, ax = plt.subplots()
                ax.plot(df["station"], df["resistivity"], marker="o")
                ax.set_xlabel("Station")
                ax.set_ylabel("Resistivity")
                ax.set_title(f"Line {selected_line}")
                ax.grid(True)
                st.pyplot(fig)
        else:
            st.info("No profiling lines recorded yet.")
    elif mode == "Sounding":
        if st.session_state.sounding:
            df = pd.DataFrame(st.session_state.sounding.values())
            st.write("Survey Info:")
            st.json({
                "Date": str(date),
                "Client": client,
                "Location": loc_name,
                "Latitude": lat,
                "Longitude": long,
                "Geology": geology,
                "Soil Type/Color": soiltype,
                "Line direction": linedir,
                "Method": prof_type,
            })
            st.write("Recorded Sounding Data:")
            st.dataframe(df)

            if not df.empty:
                fig, ax = plt.subplots()
                ax.plot(df["C1C2/2"], df["resistivity"], marker="o")
                ax.set_xlabel("C1C2/2 (AB/2)")
                ax.set_ylabel("Resistivity")
                ax.set_title("Sounding Curve")
                ax.grid(True)
                st.pyplot(fig)
        else:
            st.info("No sounding data recorded yet.")

# Export
st.markdown("---")
st.header("Export to Excel")

def create_excel(all_lines: dict, sounding: dict, sounding_meta: dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        # --- Profiling export ---
        for key, val in all_lines.items():
            sheetname = f"{key}_data"[:31]  # Excel sheet names max 31 chars
            # Write profiling metadata
            meta_rows = pd.DataFrame(list(val["meta"].items()), columns=["Field", "Value"])
            meta_rows.to_excel(writer, sheet_name=sheetname, index=False, startrow=0)

            # Then write profiling data below metadata
            df = pd.DataFrame(val["data"].values())
            df.to_excel(writer, sheet_name=sheetname, index=False, startrow=len(meta_rows) + 2)

            # Add graph in a separate sheet
            if not df.empty:
                fig, ax = plt.subplots()
                ax.plot(df["station"], df["resistivity"], marker="o")
                ax.set_xlabel("Station")
                ax.set_ylabel("Resistivity")
                ax.set_title(f"{key} Station vs Resistivity")
                ax.grid(True)
                imgdata = io.BytesIO()
                fig.savefig(imgdata, format="png", bbox_inches="tight")
                imgdata.seek(0)
                img_sheet = f"{key}_graph"[:31]
                worksheet = workbook.add_worksheet(img_sheet)
                worksheet.insert_image("B2", f"{key}.png", {"image_data": imgdata})
                plt.close(fig)

        # --- Sounding export with metadata ---
        if sounding:
            sheetname = "Sounding_Data"
            # Write metadata at top
            meta_rows_s = pd.DataFrame(list(sounding_meta.items()), columns=["Field", "Value"])
            meta_rows_s.to_excel(writer, sheet_name=sheetname, index=False, startrow=0)

            # Then write sounding data below metadata
            df_s = pd.DataFrame(sounding.values())
            df_s.to_excel(writer, sheet_name=sheetname, index=False, startrow=len(meta_rows_s) + 2)

            # Add sounding graph in separate sheet
            if not df_s.empty:
                fig, ax = plt.subplots()
                ax.plot(df_s["C1C2/2"], df_s["resistivity"], marker="o")
                ax.set_xlabel("C1C2/2 (AB/2)")
                ax.set_ylabel("Resistivity")
                ax.set_title("Sounding Curve")
                ax.grid(True)
                imgdata = io.BytesIO()
                fig.savefig(imgdata, format="png", bbox_inches="tight")
                imgdata.seek(0)
                worksheet = workbook.add_worksheet("Sounding_Graph")
                worksheet.insert_image("B2", "sound_graph.png", {"image_data": imgdata})
                plt.close(fig)

    output.seek(0)
    return output


if st.button("Download Excel"):
    if not st.session_state.lines and not st.session_state.sounding:
        st.error("No data to export")
    else:
        # Build the metadata dict to pass
        sounding_meta = {
            "Date": str(date),
            "Client": client,
            "Location": loc_name,
            "Latitude": lat,
            "Longitude": long,
            "Geology": geology,
            "Soil Type/Color": soiltype,
            "Line direction": linedir,
            "Method": mode,  # or the method used for sounding
        }
        excel_bytes = create_excel(
            st.session_state.lines,
            st.session_state.sounding,
            sounding_meta
        )
        st.download_button(
            "Download Excel File",
            data=excel_bytes,
            file_name=f"{client}_{loc_name}_{date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

