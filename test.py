import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_gsheets import GSheetsConnection
from datetime import date, timedelta, datetime
import numpy as np

conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    usecols=[0,1,2,3,4,5,6,7,8,9],
    nrows=400,
)

#Clean dataset
df = df.dropna(how="all")
df["Date of App."] = pd.to_datetime(df["Date of App."])
df.fillna(0, inplace=True)
df["Date of Resp?"] = pd.to_datetime(df["Date of Resp?"])

todayDate = date.today()

changeIndex = []
for index, row in df.iterrows():
    if(pd.Timestamp(row["Date of Resp?"]) == pd.Timestamp(datetime(1970,1,1))):
        if(pd.Timestamp(row["Date of App."] + timedelta(days=14)) <= pd.Timestamp(todayDate)):
                changeIndex.append(index)
for ind in changeIndex:
    df.at[ind, "Response?"] = "Ghosted"
    df.at[ind, "Date of Resp?"] = "N/A"
    df.at[ind, "isInstaDel?"] = "N/A"

st.title("Welcome to my engineering job application stats website!")
st.header("Rules")
st.markdown(
"""
- Only applied to jobs I met the hard requirements for (ie schooling)
- Only applied for positions that were or could be 4 months long in summer 2024
- Only applied for positions based anywhere in Canada
- Applied with a cover letter when they asked or there was an obvious spot for it
"""
)

#Const calculations
tempDf = df.loc[(df["Cover Letter?"] == "Y") | (df["Cover Letter?"] == "Yes")]
coverLetters = len(tempDf)

tempDf = df.loc[(df["IsAcc?"] == "Yes") | (df["IsAcc?"] == "Y")]
accountsMade = len(tempDf["Company"].unique())

tempDf = df.loc[((df["Response?"] == "Declined"))]
rejections = len(tempDf)

tempDf = df.loc[((df["Response?"] == "Ghosted"))]
ghosts = len(tempDf)

numberUniqueEmployers = len(df["Company"].unique())

totalDecline = ghosts + rejections

#Calculate number of Applicaations to each employer
employerCount = {}
for ind in df.index:
    if(df["Company"][ind] in employerCount):
        employerCount[df["Company"][ind]] = employerCount[df["Company"][ind]] + 1
    else:
        employerCount[df["Company"][ind]] = 1
temp = sorted(employerCount, key=employerCount.get, reverse=True)

#Make Pie chart of job types
uniqueTypes = df["Job Type"].unique()
uniqueCounts = []
for jobType in uniqueTypes:
    tempDf = df.loc[(df["Job Type"] == jobType)]
    count = len(tempDf)
    uniqueCounts.append(count)
for x in range(len(uniqueTypes)):
    percent = "%.2f" % round((uniqueCounts[x] / sum(uniqueCounts)) * 100, 2)
    if(uniqueTypes[x] == "E"):
        uniqueTypes[x] = "Electrical (" + str(uniqueCounts[x]) + ") - " + percent + "%"
    elif(uniqueTypes[x] == "Ge"):
        uniqueTypes[x] = "General Eng. (" + str(uniqueCounts[x]) + ") - " + percent + "%"
    elif(uniqueTypes[x] == "S"):
        uniqueTypes[x] = "Software (" + str(uniqueCounts[x]) + ") - " + percent + "%"
    elif(uniqueTypes[x] == "Mi"):
        uniqueTypes[x] = "Mining (" + str(uniqueCounts[x]) + ") - " + percent + "%"
    elif(uniqueTypes[x] == "E/S"):
        uniqueTypes[x] = "Computer (" + str(uniqueCounts[x]) + ") - " + percent + "%"
jobTypes, ax1 = plt.subplots()
ax1.pie(uniqueCounts, shadow=True)
ax1.axis("equal")
ax1.legend(labels=uniqueTypes)

#Make Pie chart of job outcomes
tempDf = df.loc[((df["Response?"] == "Offer"))]
offers = len(tempDf)

tempDf = df.loc[(df["Response?"] == "Cancelled")]
cancels = len(tempDf)

tempDf = df.loc[(df["Response?"] == 0)]
pending = len(tempDf)

jobOutcomes, ax1 = plt.subplots()
labels = ["Rejected", "Ghosted", "Cancels", "Offer", "Pending"]
counts = [rejections, ghosts, cancels, offers, pending]

for x in range(len(labels)):
    percent = "%.2f" % round((counts[x] / sum(counts)) * 100, 2)
    labels[x] = labels[x] + " (" + str(counts[x]) + ") - " + percent + "%"

ax1.pie(counts, shadow=True)
ax1.axis("equal")
ax1.legend(labels=labels)

#Website Display
col1, col2 = st.columns(2)

col3, col4 = st.columns(2)

with col1:
    st.pyplot(jobTypes)

with col2:
    st.header("Applications")
    st.text("Jobs applied for: " + str(len(df)))
    st.text("Cover Letters sent: " + str(coverLetters))
    st.text("Hiring accounts made: " + str(accountsMade))
    st.text("Most applications to one company: " + str(employerCount[temp[0]]))
    st.text("Unique companies applied to: " + str(numberUniqueEmployers))

with col3:
    st.header("Results")
    st.text("Times ghosted (no rejection email): " + str(ghosts))
    st.text("Times rejected: " + str(rejections))
    st.text("Total Non-offers: " + str(rejections + ghosts))

with col4:
    st.pyplot(jobOutcomes)