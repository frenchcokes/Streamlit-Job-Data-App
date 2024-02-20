import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    usecols=[0,1,2,3,4,5,6,7,8,9],
    nrows=400,
)

#removes bad
df = df.dropna(how="all")

st.text("Welcome to my non-real engineering job application stats website!")

st.text("Jobs applied for: " + str(len(df)))

rejections = 0
tempDf = df.loc[((df["Response?"] == "Declined"))]
rejections = len(tempDf)

ghosts = 0
tempDf = df.loc[((df["Response?"] == "Ghosted"))]
ghosts = len(tempDf)

coverLetters = 0
tempDf = df.loc[(df["Cover Letter?"] == "Y") | (df["Cover Letter?"] == "Yes")]
coverLetters = len(tempDf)

#Make Pie chart of job types
uniqueTypes = df["Job Type"].unique()
uniqueCounts = []
for jobType in uniqueTypes:
    count = 0
    tempDf = df.loc[(df["Job Type"] == jobType)]
    count = len(tempDf)
    uniqueCounts.append(count)
for x in range(len(uniqueTypes)):
    percent = "%.2f" % round((uniqueCounts[x] / sum(uniqueCounts)) * 100, 2)
    if(uniqueTypes[x] == "E"):
        uniqueTypes[x] = "Electrical - " + percent + "%"
    elif(uniqueTypes[x] == "Ge"):
        uniqueTypes[x] = "General Eng. - " + percent + "%"
    elif(uniqueTypes[x] == "S"):
        uniqueTypes[x] = "Software - " + percent + "%"
    elif(uniqueTypes[x] == "Mi"):
        uniqueTypes[x] = "Mining - " + percent + "%"
    elif(uniqueTypes[x] == "E/S"):
        uniqueTypes[x] = "Computer - " + percent + "%"

fig1, ax1 = plt.subplots()
ax1.pie(uniqueCounts, shadow=True)
ax1.axis("equal")
ax1.legend(labels=uniqueTypes)
st.pyplot(fig1)

st.text("Cover Letters sent: " + str(coverLetters))
st.text("Times ghosted (Employer didn't respond with rejection email): " + str(ghosts))
st.text("Times rejected: " + str(rejections))
st.text("Total Non-offers: " + str(rejections + ghosts))

#Do not commit me not commented out!
#st.dataframe(df)
#End do not commit