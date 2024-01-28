import json
import time

import requests
import numpy as np
import pandas as pd
import pyarrow as pa
import matplotlib.pyplot as plt

from reportlab.pdfgen import canvas
from reportlab.lib import colors, units
from reportlab.lib.pagesizes import letter


def query_data():
    '''this function returns json data from the api response'''
    pg = 1
    pp = 20000
    urls = [
        f"https://api.worldbank.org/v2/country/all/indicators/SH.STA.BASS.ZS?date=1960:2024&source=2&format=json&per_page={pp}&page={pg}",
    ]

    # variables for info on pages and entries from api response 
    data = []
    total = 0

    for url in urls:
        req = requests.get(url)
        if req.status_code != requests.codes.ok:
            print(f"request error {req.status_code}")

        # get data from api response
        resp = req.json()

        # get info on pages and entries from api response
        pages, entries = resp[0]['pages'], resp[0]['total']
        total += entries
        print(f"{pages} pages with {entries} entries")

        # append data entries from api response
        objs = resp[1]
        print(f"response has {len(objs)} objects")
        for i in range(len(objs)):
            objs[i]["country_id"] = objs[i]["country"]["id"]
            data.append(objs[i])
        time.sleep(2) # respect possible api rate limits

    return data

def load_data(fp):
    '''this function returns json data from a json file'''
    with open(fp, "r") as source:
        data = json.load(source)

    return data

def wrangle_data(data):
    '''this function returns the data as a useful dataframe'''
    df = pd.DataFrame(data)
    df = df.set_index(["date"])

    # get list of countries
    countries = sorted(set(df["country_id"]))

    # create sub dataframe for analysis
    sub = pd.DataFrame()

    # concat series for each country as column
    for country in countries:
        ds = df["value"][df["country_id"] == country]
        sub = pd.concat([sub, ds.rename(country)], axis=1)
    sub.sort_index(inplace=True)

    return sub

def visualize_data(df, jpg):
    '''this function generates the figure & saves as a png'''
    fig, ax = plt.subplots(figsize=(4.8,3), layout='constrained')
    ax.plot(df.index, df['XM'], label='low income')
    ax.plot(df.index, df['XN'], label='lower middle income')
    ax.plot(df.index, df['XT'], label='upper middle income')
    ax.plot(df.index, df['XD'], label='high income')
    ax.plot(df.index, df['1W'], label='worldwide')
    ax.set_xlabel('Year')
    xstart, xend = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(xstart, xend, 3))
    ax.set_ylabel('% of population')
    ax.set_title('Figure 1: Access to basic sanitation')
    ax.legend(loc="best")

    plt.savefig(jpg)

def report_data(jpg):
    '''this function generates a pdf report with a png image'''
    file_name = "TechnicalExercisePartI.pdf"
    doc_title = 'Technical Exercise Part I'
    title = 'Technical Exercise Part I'
    #sub_title = 'Explore relations among access to sanitaion across time and country income groups'
    doc_text = [
        "Figure 1 displays access to basic sanitation services grouped by country income groups. ",
        "Visual analysis of Figure 1 suggests that (i) access to basic sanitation is positively ",
        "related to a country's income level, (ii) middle income countries are catching up to high ",
        "income countries with respect to the percentag of the population with access to basic ",
        "sanitation services, and (iii) low income countries lag behind middle income countries ",
        "with basic access to sanitation among low income countries in 2022 near that of lower ",
        "middle income countries in 2000. In particular, access to basic sanitation increased ",
        "from 55.4 percent in 2000 to 80.6 percent in 2022 worldwide, which was primarily driven ",
        "by lower and upper middle income countries; increased from 19.5 percent in 2000 to 31.4 ",
        "percent in 2022 among low income countries; increased from 31.6 percent to 72.5 percent ",
        "among lower middle income countries; increased from 63.8 percent to 93.4 percent among ",
        "upper middle income countries; and increased from 98.6 percent to 99.0 percent among ",
        "high income countries.",
    ]
    #doc_image = "chart.jpg"

    # create pdf object & set document title
    pdf = canvas.Canvas(file_name, pagesize=letter)
    pdf.setTitle(doc_title)

    # insert title
    pdf.setFont('Helvetica', 28)
    pdf.drawString(1*units.inch, 10*units.inch, title)

    ## insert subtitle
    #pdf.setFont('Helvetica', 14)
    #pdf.drawString()

    # insert document text
    text = pdf.beginText(1*units.inch, 9*units.inch)
    text.setFont('Helvetica', 12)
    for line in doc_text:
        text.textLine(line)
    pdf.drawText(text)

    # insert document image
    pdf.drawInlineImage(jpg, 1*units.inch, 1*units.inch)

    # save the pdf object to a file
    pdf.showPage()
    pdf.save()


# run program to generate report
data = query_data()
df = wrangle_data(data)
visualize_data(df, "fig1.jpg")
report_data("fig1.jpg")
