import streamlit as st
import simpy
import random
import statistics
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Simulasi Sistem Piket IT Del", layout="wide")
st.title("Simulasi Sistem Piket Mahasiswa IT Del")

# ======================
# INPUT
# ======================
jumlah_ompreng = st.slider("Jumlah Ompreng", 60, 300, 180)

# ======================
# DATA
# ======================
data = {
    "Lauk": [],
    "Angkat": [],
    "Nasi": [],
    "Total": []
}
waktu_selesai = []

# ======================
# PROSES OMPRENG
# ======================
def proses_ompreng(env, lauk, angkat, nasi):
    mulai = env.now

    with lauk.request() as req:
        yield req
        t = random.uniform(0.5, 1)
        data["Lauk"].append(t)
        yield env.timeout(t)

    with angkat.request() as req:
        yield req
        t = random.uniform(0.33, 1)
        data["Angkat"].append(t)
        yield env.timeout(t)

    with nasi.request() as req:
        yield req
        t = random.uniform(0.5, 1)
        data["Nasi"].append(t)
        yield env.timeout(t)

    total = env.now - mulai
    data["Total"].append(total)
    waktu_selesai.append(env.now)

# ======================
# GENERATOR
# ======================
def generator(env, lauk, angkat, nasi):
    for _ in range(jumlah_ompreng):
        env.process(proses_ompreng(env, lauk, angkat, nasi))
        yield env.timeout(0.1)

# ======================
# SIMULASI
# ======================
env = simpy.Environment()
lauk = simpy.Resource(env, capacity=2)
angkat = simpy.Resource(env, capacity=2)
nasi = simpy.Resource(env, capacity=3)

env.process(generator(env, lauk, angkat, nasi))
env.run()

# ======================
# OUTPUT
# ======================
st.subheader("📌 Ringkasan Hasil Simulasi")

if waktu_selesai:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Waktu Piket (menit)", round(max(waktu_selesai), 2))
    col2.metric("Rata-rata per Ompreng", round(statistics.mean(data["Total"]), 2))
    col3.metric("Waktu Tercepat", round(min(data["Total"]), 2))
    col4.metric("Waktu Terlama", round(max(data["Total"]), 2))

    df = pd.DataFrame(data)

    st.subheader("📊 Distribusi Waktu Penyelesaian Ompreng")
    st.plotly_chart(px.histogram(df, x="Total", nbins=30), use_container_width=True)

    st.subheader("📈 Progres Penyelesaian Ompreng")
    df_prog = pd.DataFrame({
        "Waktu": sorted(waktu_selesai),
        "Ompreng Selesai": range(1, len(waktu_selesai) + 1)
    })
    st.plotly_chart(px.line(df_prog, x="Waktu", y="Ompreng Selesai"),
                    use_container_width=True)

    st.subheader("📉 Rata-rata Waktu per Tahap (Bottleneck)")
    df_mean = df[["Lauk", "Angkat", "Nasi"]].mean().reset_index()
    df_mean.columns = ["Tahap", "Waktu Rata-rata"]
    st.plotly_chart(px.bar(df_mean, x="Tahap", y="Waktu Rata-rata"),
                    use_container_width=True)
else:
    st.warning("Simulasi belum menghasilkan data.")
