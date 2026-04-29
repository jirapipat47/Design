import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pile Eccentric Calculator", layout="centered")

st.title("📐 โปรแกรมคำนวณเสาเข็มเยื้องศูนย์")
st.write("กรอกข้อมูลให้ครบ ระบบจะคำนวณค่าแรงแต่ละเสาให้อัตโนมัติ")

# -------------------------
# INPUT GLOBAL LOAD
# -------------------------
st.header("🔹 แรงกระทำ")

P = st.number_input("แรงกดรวม P (kN)", value=1000.0)
Mx = st.number_input("โมเมนต์รอบแกน X (kN-m)", value=0.0)
My = st.number_input("โมเมนต์รอบแกน Y (kN-m)", value=0.0)

# -------------------------
# NUMBER OF PILES
# -------------------------
st.header("🔹 จำนวนเสาเข็ม")
n = st.number_input("จำนวนเสาเข็ม", min_value=1, step=1)

# -------------------------
# INPUT TABLE
# -------------------------
st.header("🔹 พิกัดเสาเข็ม")

data = pd.DataFrame({
    "Pile": [f"P{i+1}" for i in range(n)],
    "X (m)": [0.0]*n,
    "Y (m)": [0.0]*n
})

edited_data = st.data_editor(data, use_container_width=True)

# -------------------------
# CALCULATION
# -------------------------
if st.button("🚀 คำนวณ"):
    
    x = edited_data["X (m)"].values
    y = edited_data["Y (m)"].values
    
    # centroid
    x_bar = np.mean(x)
    y_bar = np.mean(y)
    
    # shift to centroid
    xi = x - x_bar
    yi = y - y_bar
    
    # eccentricity
    ex = My / P if P != 0 else 0
    ey = Mx / P if P != 0 else 0
    
    # denominator
    sum_x2 = np.sum(xi**2)
    sum_y2 = np.sum(yi**2)
    
    Pi = []
    
    for i in range(n):
        pi = (P / n)
        
        if sum_y2 != 0:
            pi += (Mx * yi[i]) / sum_y2
        
        if sum_x2 != 0:
            pi += (My * xi[i]) / sum_x2
        
        Pi.append(pi)
    
    result = edited_data.copy()
    result["Xi"] = xi
    result["Yi"] = yi
    result["Pi (kN)"] = Pi
    
    # -------------------------
    # OUTPUT
    # -------------------------
    st.header("📊 ผลลัพธ์")
    
    st.write(f"📌 ex = {ex:.4f} m")
    st.write(f"📌 ey = {ey:.4f} m")
    
    st.dataframe(result, use_container_width=True)
    
    st.success("✅ คำนวณเรียบร้อยแล้ว")
