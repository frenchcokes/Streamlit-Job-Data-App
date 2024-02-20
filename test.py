import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    worksheet="Job Applications",
    ttl="0",
    usecols=[3, 5],
    nrows=200,
)

f = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

st.table(f)