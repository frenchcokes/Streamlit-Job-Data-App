import streamlit as st
import pandas as pd
import os
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    usecols=[0,1,2,3,4,5,6,7,8,9],
    nrows=400,
)

#removes bad
df = df.dropna(how="all")

st.text("Welcome to my non-real job application stats website!")

st.text("Applications sent: " + str(len(df)))

rejections = 0
tempDf = df.loc[((df["Response?"] == "Declined"))]
rejections = len(tempDf)

ghosts = 0
tempDf = df.loc[((df["Response?"] == "Ghosted"))]
ghosts = len(tempDf)

coverLetters = 0
tempDf = df.loc[(df["Cover Letter?"] == "Y") | (df["Cover Letter?"] == "Yes")]
coverLetters = len(tempDf)

st.text("Cover Letters sent: " + str(coverLetters))
st.text("Times ghosted (Employer didn't respond with rejection email): " + str(ghosts))
st.text("Times rejected: " + str(rejections))
st.text("Total Non-offers: " + str(rejections + ghosts))

#Do not commit me not commented out!
#st.dataframe(df)
#End do not commit