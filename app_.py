import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime
import matplotlib.pyplot as plt
import xlsxwriter
from streamlit_searchbox import st_searchbox

st.set_page_config(page_title="RESISTIVITY DATA VIEWER", layout="wide")
st.image("https://bebpl.com/wp-content/uploads/2023/07/BLUE-ENERGY-lFINAL-LOGO.png", width=200)

# --- CSS for gradient background and nicer layout ---
st.markdown(
    """
    <style>
    .stApp {
      background-image: url("https://www.color-hex.com/palettes/4719.png");
      background-size: cover;
      background-position: center;
      /* You can keep a gradient overlay by layering it */
      /* background-image:
         linear-gradient(90deg, rgba(160,68,214,0.5), rgba(113,196,255,0.5)),
         url("https://example.com/your-image.jpg"); */
      color: black;
    }
    .big-title {
      font-size: 40px;
      font-weight: 700;
      text-align: center;
      padding: 20px 0;
    }
    .card {
      background: rgba(255,255,255,0.06);
      padding: 12px;
      border-radius: 10px;
    }
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
        tables[200] = pd.read_excel("geom_200.xlsx")
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
            
    '''
    
    elif mode == "Sounding":
        if "sounding" in GEOM_TABLES:                 # First, try to get the factor from the table
            df = GEOM_TABLES["sounding"]
            match = df[(df["C1C2"] == C1C2) & (df["P1P2"] == P1P2)]
            if not match.empty:
                return float(match["GeometricFactor"].values[0])
        # If we reach here, table doesn't have the factor or table missing
        # Use the custom formula instead of default 1.0
            if  prof_type == "Schlumberger":
                #prof_type = st.selectbox("Method", ["Schlumberger", "Wenner","Dipole-Dipole"])
                try:
                    # Note: C1C2 and P1P2 expected as floats
                    # your formula: 3.1428 * ( ((C1C2/2)^2 - (P1P2)^2) / (2 * P1P2) )
                    # In Python '^' is bitwise XOR; for power use '**'
                    geom = 3.1428 * ( ((C1C2_val) ** 2 - (P1P2_val) ** 2) / (2 * P1P2_val) )
                    return float(geom)
                except Exception as e:
                    # If formula fails (e.g. P1P2 is zero or None), fallback to 1.0
                    return 1.0
            elif prof_type == "Wenner":
                try:
                    # Note: C1C2 and P1P2 expected as floats
                    # your formula: 3.1428 * ( ((C1C2/2)^2 - (P1P2)^2) / (2 * P1P2) )
                    # In Python '^' is bitwise XOR; for power use '**'
                    C1C2_val = None
                    geom = 2*3.1428 * (P1P2_val) 
                    return float(geom)
                except Exception as e:
                    # If formula fails (e.g. P1P2 is zero or None), fallback to 1.0
                    return 1.0
                    
            elif prof_type == "Dipole-Dipole":
                try:
                    geom = 3.1428 * C1C2_val*(C1C2_val+1)*(C1C2_val+2)*(P1P2_val) 
                    return float(geom)
                except Exception as e:
                    # If formula fails (e.g. P1P2 is zero or None), fallback to 1.0
                    return 1.0           
            
    else:
        return 1.0

   
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
    mode = st.radio("Choose mode", ["Profiling", "Sounding"],horizontal=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col1:
    st.markdown('<div class="card" style="margin-top:12px">', unsafe_allow_html=True)
    st.subheader("Survey Info")
    date = st.date_input("Survey date", value=datetime.today()).strftime("%d-%m-%Y")
    client = st.text_input("Client name",placeholder="Rudra Venkatesh")
    loc_name = st.text_input("Location Name",placeholder="Village or VES N0.")
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
        prof_type = st.selectbox("Method", ["Gradient", "Other"])
        C1C2 = st.number_input("Enter C1C2 distance (e.g. 300 or 400)", min_value=1.0, value=400.0, step=100.0)
        P1P2 = st.number_input("Enter P1P2 interval (e.g. 5)", min_value=1.0, value=10.0, step=1.0)

        st.subheader("Line Setup")
        line_number = st.text_input("Line number",placeholder="L0/N50/S50/E50/W50/NE50/SW50/SE50/NW50")
        
        
        #station = st.number_input("Station",value= None,placeholder="35/-35", step=5)
        
        stations_400 = [
                        "5","15","25","35","45","55","65","75","85","95","105","115","125","135","145","155","165",
                       "-5","-15","-25","-35","-45","-55","-65","-75","-85","-95","-105","-115","-125","-135","-145","-155","-165"
                        ]
                        
        stations_300 = [
                        "5","15","25","35","45","55","65","75","85","95","105","115","125",
                       "-5","-15","-25","-35","-45","-55","-65","-75","-85","-95","-105","-115","-125"
                        ]


        stations_200  = [
                        "5","15","25","35","45","55","65","75",
                        "-5","-15","-25","-35","-45","-55","-65","-75"
                        ]
        
        def search_nums(term: str) -> list[str]:
            if C1C2 == 400:
                options = stations_400
            elif C1C2 == 300:
                options = stations_300
            elif C1C2 == 200:
                options = stations_200
            else:
                return []  # Return empty list if C1C2 is neither 400 nor 300

            if not term:
                return []  # Return empty list if term is empty

            term = term.lower()  # Convert term to lowercase for case-insensitive matching
            return [n for n in options if n.lower().startswith(term)]
           
        st.markdown('###### <span style="color: darkred;">Station</span>', unsafe_allow_html=True)
        station = st_searchbox( 
            search_function=search_nums,
            placeholder="-35/35",
            key="num_search",label=None
        )

        if station is not None and station != "":
            try:
                station = float(station)
            except ValueError:
                st.error(f"Could not convert '{station}' to float.\n Please select proper Value")
                station = None
        else:
            station = None
               
        #resistance = st.number_input("Resistance (ohms)", value=0.0,format="%.5f")
        
        #resistance = st.text_input("Resistance (ohms)")
        
        resistance = st.text_input("Resistance (ohms)", key="resistance")
        
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
        prof_type = st.radio("Method", ["Schlumberger", "Wenner","Dipole-Dipole"],horizontal=True)
        
        #C1C2_val = st.number_input("Enter C1C2 (AB spacing)", min_value=1.0, value=10.0, step=1.0)
        
        if prof_type == "Schlumberger":
            AB_2 = [1,1.5,2,2.5,3,3.5,4,5,6,7,8,10,12,15,20,25,30,35,40,50,60,70,80,100,
                    120,150,160,180,200,250,300,350,400,500,600,700,800,1000,1200,1500,
                    1750,2000,2500,3000]
            MN_2 = ["0.5","1","2","5","10","20","50"]
            #C1C2_val = st.text_input("C1C2/2 (AB/2)",placeholder="1.5")
            C1C2_val = st.selectbox("C1C2/2 (AB/2)",options=AB_2+["Other"])    
            if C1C2_val == "Other":
                C1C2_val_manual = st.text_input("C1C2/2 (AB/2)",placeholder="1.5")
                if C1C2_val_manual:
                    C1C2_val = C1C2_val_manual
            try:
                C1C2_val = float(C1C2_val)
                C1C2_val = round(C1C2_val,6)
            except:
                C1C2_val = None
                        
            #P1P2_val = st.number_input("Enter P1P2 (MN spacing)", min_value=1.0, value=1.0, step=1.0)
            
            #P1P2_val = st.text_input("P1P2/2 (MN/2)",placeholder="0.5")
            P1P2_val = st.selectbox("P1P2/2 (MN/2)",options=MN_2+["Other"]) #st.text_input("P1P2/2 (MN/2)",placeholder="0.5")
            if P1P2_val == "Other":
                P1P2_val_manual = st.text_input("P1P2/2 (MN/2)",placeholder="0.5")
                if P1P2_val_manual:
                    P1P2_val = P1P2_val_manual
            try:
                P1P2_val = float(P1P2_val)
                P1P2_val = round(P1P2_val,6)
            except:
                P1P2_val = None
                
        elif prof_type == "Wenner":
            C1C2_val = None
            P1P2_val = st.text_input("P1P2 or a",placeholder="1")
            try:
                P1P2_val = float(P1P2_val)
                P1P2_val = round(P1P2_val,6)
            except:
                P1P2_val = None 
                
        elif prof_type == "Dipole-Dipole":
            
            C1C2_val = st.text_input("n",placeholder="1")
            try:
                C1C2_val = float(C1C2_val)
                C1C2_val = round(C1C2_val,6)
            except:
                C1C2_val = None
            #P1P2_val = st.number_input("Enter P1P2 (MN spacing)", min_value=1.0, value=1.0, step=1.0)
            
            P1P2_val = st.text_input("a",placeholder="1")
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
            #gfactor = get_geometric_factor("Sounding", C1C2_val, P1P2=P1P2_val)
            if prof_type == "Schlumberger":
                gfactor = 3.1428 * ( ((C1C2_val) ** 2 - (P1P2_val) ** 2) / (2 * P1P2_val) )
                gfactor = float(gfactor)
                                   
            elif prof_type == "Wenner": 
                gfactor = 2*3.1428 * (P1P2_val)
                gfactor = float(gfactor)
                
            elif prof_type == "Dipole-Dipole":
                gfactor = 3.1428 * C1C2_val*(C1C2_val+1)*(C1C2_val+2)*(P1P2_val)
                gfactor = float(gfactor)
                
            #get_geometric_factor(mode, C1C2, line_number=None, station=None, P1P2=None)
            #resistivity = round(resistance * gfactor, 6)
            
            if resistance is None:
                st.error("⚠️ Please enter a proper resistance value.")
                resistivity = None
 
            elif gfactor is None:
                st.error("⚠️ Please enter a proper gfactor value.")
                resistivity = None
                    
            else:
                    resistivity = round(resistance * gfactor, 6)
            if prof_type == "Schlumberger":
                st.session_state.sounding[(C1C2_val, P1P2_val)] = {
                    "C1C2/2": C1C2_val,
                    "P1P2/2": P1P2_val,
                    "resistance": resistance,
                    "gfactor": gfactor,
                    "resistivity": resistivity,
                    "remark":r_mark
                }
                st.success(f"Recorded Sounding: C1C2/2={C1C2_val}, P1P2/2={P1P2_val}")
            elif prof_type == "Wenner":   
                st.session_state.sounding[(C1C2_val, P1P2_val)] = {
                    #"C1C2/2": C1C2_val,
                    "a": P1P2_val,
                    "resistance": resistance,
                    "gfactor": gfactor,
                    "resistivity": resistivity,
                    "remark":r_mark
                }
                st.success(f"Recorded Sounding: a = {P1P2_val}")
            elif  prof_type == "Dipole-Dipole":  
                st.session_state.sounding[(C1C2_val, P1P2_val)] = {
                    "n": C1C2_val,
                    "a": P1P2_val,
                    "resistance": resistance,
                    "gfactor": gfactor,
                    "resistivity": resistivity,
                    "remark":r_mark
                }                
                st.success(f"Recorded Sounding: n={C1C2_val}, a={P1P2_val}")
              
            
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
                #prof_type = st.radio("Method", ["Schlumberger", "Wenner","Dipole-Dipole"],horizontal=True)
                
                if prof_type == "Schlumberger":
                    
                    #ax.plot(df["C1C2/2"], df["resistivity"], marker="o")   this in normal graph
                    #for double log sheet
                    ax.loglog(df["C1C2/2"], df["resistivity"],linestyle='-',linewidth=1.0,color='darkblue', marker="o",markersize=4,markerfacecolor='red',markeredgecolor='red')
                    ax.set_xlabel("<----- C1C2/2 (AB/2) ----->")
                    ax.set_title("Schlumberger-Sounding Curve")
                    
                    
                elif prof_type == "Wenner":
                    ax.loglog(df["a"], df["resistivity"], linestyle='-',linewidth=1.0,color='darkblue', marker="o",markersize=4,markerfacecolor='red',markeredgecolor='red')
                    ax.set_xlabel("<----- a ----->")
                    ax.set_title("Wenner-Sounding Curve")
                
                elif prof_type == "Dipole-Dipole":
                    ax.loglog((df["a"]*df["n"]), df["resistivity"],linestyle='-',linewidth=1.0,color='darkblue', marker="o",markersize=4,markerfacecolor='red',markeredgecolor='red')
                    ax.set_xlabel("n x a ----->")
                    ax.set_title("Dipole-Dipole_Sounding Curve")   
                    
                ax.set_ylabel("<----- Resistivity ----->")
                ax.set_xscale('log')
                ax.set_yscale('log')
                ax.minorticks_on()
                ax.grid(True, which="both", linestyle="--", linewidth=0.4)
                #ax.grid(True)
                st.pyplot(fig)
        else:
            st.info("No sounding data recorded yet.")

# Exports
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
                if prof_type == "Schlumberger":
                    ax.loglog(df_s["C1C2/2"], df_s["resistivity"], linestyle='-',linewidth=1.0,color='darkblue', marker="o",markersize=4,markerfacecolor='red',markeredgecolor='red')
                    ax.set_xlabel("<----- C1C2/2 (AB/2) ----->")
                    ax.set_title("Schlumberger-Sounding Curve")
                    
                
                elif prof_type == "Wenner":
                    ax.loglog(df_s["a"], df_s["resistivity"], linestyle='-',linewidth=1.0,color='darkblue', marker="o",markersize=4,markerfacecolor='red',markeredgecolor='red')
                    ax.set_xlabel("<----- a ----->")
                    ax.set_title("Wenner-Sounding Curve")
                
                elif prof_type == "Dipole-Dipole":
                    ax.loglog((df_s["a"]*df_s["n"]), df_s["resistivity"], linestyle='-',linewidth=1.0,color='darkblue', marker="o",markersize=4,markerfacecolor='red',markeredgecolor='red')
                    ax.set_xlabel(" <----- n x a ----->")
                    ax.set_title("Dipole-Dipole Sounding Curve")
                    
                ax.set_ylabel("<----- Resistivity ----->")    
                ax.set_xscale('log')
                ax.set_yscale('log')
                ax.minorticks_on()
                ax.grid(True, which="both", linestyle="--", linewidth=0.4)
                #ax.grid(True)
                imgdata = io.BytesIO()
                fig.savefig(imgdata, format="png", bbox_inches="tight")
                imgdata.seek(0)
                
                worksheet = workbook.add_worksheet("Sounding_Graph")
                worksheet.insert_image("B2", "sound_graph.png", {"image_data": imgdata})
                plt.close(fig)

    output.seek(0)
    return output



if st.button("Export"):
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
            "Method": prof_type,  # or the method used for sounding
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",icon="📥"
        )




