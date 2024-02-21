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

#Const calculations
totalJobs = len(df)

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

daysPassed = (pd.Timestamp(todayDate) - pd.Timestamp(df["Date of App."][0])).days
averageApplications = "%.2f" % round((totalJobs / daysPassed), 2)

#Calculate number of Applicaations to each employer
employerCount = {}
for ind in df.index:
    if(df["Company"][ind] in employerCount):
        employerCount[df["Company"][ind]] = employerCount[df["Company"][ind]] + 1
    else:
        employerCount[df["Company"][ind]] = 1
temp = sorted(employerCount, key=employerCount.get, reverse=True)

#Create response time histogram
tempDf = df.loc[(df["Response?"] == "Declined") | (df["Response?"] == "Cancelled")]
arr = []
for index in tempDf.index:
    arr.append((pd.Timestamp(tempDf["Date of Resp?"][index]) - pd.Timestamp(tempDf["Date of App."][index])).days)
responseHist, ax1 = plt.subplots()
ax1.hist(arr, bins=15, histtype='bar', ec = "black")
ax1.set_xlabel("Days After Sending Application")
ax1.set_ylabel("Count")
ax1.set_xticks(range(0, max(arr), 5))
ax1.margins(x=0)

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
st.title("Welcome to my engineering job application stats website!")
st.header("Rules")
st.markdown(
"""
- Aimed to apply for 4 applications a day (Started on 2023-12-23)
- Only applied to jobs I met the hard requirements for (ie schooling)
- Only applied for positions that were or could be 4 months long in summer 2024
- Only applied for positions based anywhere in Canada
- Applied with a cover letter when they asked or there was an obvious spot for it
- Data begins officially on 2023-09-20 before I set a quota for 4 a day. This is reflected in the applications per day.
"""
)

st.header("Applications")
col1, col2, col3 = st.columns([2,1,1])

st.header("Response Times of Employers")
st.pyplot(responseHist)

st.header("Results")
col4, col5, col6 = st.columns([1,1,2])

with col1:
    st.subheader("Types of Jobs Applied to")
    st.pyplot(jobTypes)

with col2:
    st.metric("Total Applications", (totalJobs))
    st.metric("Hiring Accounts Made", (accountsMade))
    st.metric("Applications per Day", averageApplications )

with col3:
    st.metric("Cover Letters", (coverLetters))
    st.metric("Unique Companies", (numberUniqueEmployers))
    st.metric("Most App. to a company",(employerCount[temp[0]]))

with col4:
    st.metric("Times Ghosted", ghosts)
    st.metric("Total Offers", str(offers))

with col5:
    st.metric("Times Rejected ", rejections)
    st.metric("Total Non-offers", str(rejections + ghosts + cancels))

with col6:
    st.subheader("Current Status of App.")
    st.pyplot(jobOutcomes)

st.header("Definitions")
st.markdown(
"""
- General Eng. - When a position doesn't specify what kind of engineering and it isn't obvious.
- Ghosted - When there is no response 2 weeks from the application date.
- Rejected - Rejected.
- Cancel - When they send a message saying they aren't hiring for the position.
- Offer - Offer of employment.
- Pending - When it isn't ghosted or declined.
"""
)
