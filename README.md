# Elevatr - Equity Investing Platform

## Introduction

Welcome to Elevatr, an educational equity investing platform designed to help everyday people and students learn investing fundamentals through hands-on practice. This project combines portfolio management, analytics, and educational tools to make equity investing accessible and understandable.

### Features

- Adjustable transactions (`transactions.json`)for when a stock is bought or sold
- Daily updates on all of the portfolio's positions
- Generation of a weekly report
- Tracking of dividends
- Tracking of cash position

## Motivation and Background

This project was initiated to make equity investing education accessible to everyone. It serves two primary audiences:

1. **General Users**: Learning basic financial literacy and portfolio management with enhanced analytics
2. **Students & Institutions**: Practicing trading skills through simulated and real-money portfolios, with support for student-managed funds

## How does it work?

- Download the latest data of all of the positions by running `python3 main.py -download`
  This uses the Yahoo Finance package (not the api technically) to get the latest data of all the stocks and puts them into `downloaded_data.pkl`

- Download the latest exchange rate data by running `python3 update_data.py` and then `python3 convert_csv.py`
  This get the latest exchange rate data from the ECB's published historical data. By running `convert_csv.py` it will merge that downloaded data with the `ecb_daily.pkl` which stores the daily fx data going back to the early 2000s.
  _note_
  `update_data.py` is a shell script for now but I'm working on making it into a python script to also make it work on Windows. In the future `main.py` should be able to update the data (like It is done now with the -download flag for stock data) without having to run all those files on their own.

- With all the data updated you can run `python3 main.py --daily-dump or --weekly-report` to produce the daily dump or weekly report respectively.

- I'm using cron and rclone to run the script at specified times and then upload the data to cloud storage.

## Installation and Setup

To set up the Trading Software, follow these steps:

1. Clone the repository:

`git clone https://github.com/matat99/portfolio_mgr.git`

2. Install the required packages:
   `cd portfolio_mgr`

`pip install -r requirements.txt`

## To Do

- [ ] Make the README actually useful
- [ ] Implement a way to track stock splits
- [ ] Make this work on Windows
- [ ] Incorporate some modeles
- [ ] Maybe a UI?
- [ ] Make the fx data update less tedious.
- [ ] Clean up unused imports and de-bloat requirements.txt.

## Contributors

This Project was created by Maciej Miazek (mam00961@students.stir.ac.uk), further developed by Raj Aryan Upadhyaya (upadhyra@tcd.ie)
