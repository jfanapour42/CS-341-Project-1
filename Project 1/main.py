#
# Jordan Fanapour
# Fall 2022
# Computer Science 341
# Project 1
#
# This program will utilize python and sql to prompt a user
# grab data from the CTA2 database and print the data to
# the console. The user will be prompted to input a number
# 1 through 9 and using python the program will execute the
# corresponding code. Each vallid user command will do a specific
# task ranging from soley outputing the data to the console to
# prompting the user to graph the data to a graph in the output
# tab. Once the command is done executing, the program will prompt
# the user to input another valid command.
#

import sqlite3
import matplotlib.pyplot as plt


##################################################################
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
  dbCursor = dbConn.cursor()

  print("General stats:")

  # Print number of stations
  sql = "Select count(*) From Stations;"
  dbCursor.execute(sql)
  row = dbCursor.fetchone()
  print("  # of stations:", f"{row[0]:,}")

  # Print number of stops
  sql = "Select count(*) From Stops;"
  dbCursor.execute(sql)
  row = dbCursor.fetchone()
  print("  # of stops:", f"{row[0]:,}")

  # Print number of total ride entries
  sql = "Select count(*) From Ridership;"
  dbCursor.execute(sql)
  row = dbCursor.fetchone()
  print("  # of ride entries:", f"{row[0]:,}")

  # Print date range of database
  sql = """Select MIN(strftime('%Y-%m-%d', Ride_Date)),     
           MAX(strftime('%Y-%m-%d', Ride_Date)) 
           From Ridership;"""
  dbCursor.execute(sql)
  row = dbCursor.fetchone()
  print("  Date Range: %s - %s" % (row[0], row[1]))

  # Print total number of riders
  sql = "Select Sum(Num_Riders) From Ridership;"
  dbCursor.execute(sql)
  row = dbCursor.fetchone()
  totalRiders = row[0]
  print("  Total ridership:", f"{row[0]:,}")

  # Print total number of riders on weekdays
  sql = """Select Sum(Num_Riders) From Ridership 
           Where Type_Of_Day = 'W';"""
  dbCursor.execute(sql)
  row = dbCursor.fetchone()
  weekdayRiders = row[0]
  perc = getPercentage(weekdayRiders, totalRiders)
  print("  Weekday ridership: %s (%.2f%%)" %(f"{row[0]:,}", perc))

  # Print total number of riders on saturdays
  sql = """Select Sum(Num_Riders) From Ridership
           Where Type_Of_Day = 'A';"""
  dbCursor.execute(sql)
  row = dbCursor.fetchone()
  saturdayRiders = row[0]
  perc = getPercentage(saturdayRiders, totalRiders)
  print("  Saturday ridership: %s (%.2f%%)" %(f"{row[0]:,}", perc))

  # Print total number of riders on sundays and holidays
  sql = """Select Sum(Num_Riders) From Ridership 
           Where Type_Of_Day = 'U';"""
  dbCursor.execute(sql)
  row = dbCursor.fetchone()
  sunAndHolidayRiders = row[0]
  perc = getPercentage(sunAndHolidayRiders, totalRiders)
  print("  Sunday/Holiday ridership: %s (%.2f%%)" %
        (f"{row[0]:,}", perc))

#
# loopCommandRequest
#
# Given a connection to the CTA database, prompt user to
# input commands numbered 1 through 9 and then call
# corresponding functions to execute them
#
def loopCommandRequest(dbConn):
  # Dictionary with number mapped to fuction name
  commands = {
      1: command1,
      2: command2,
      3: command3,
      4: command4,
      5: command5,
      6: command6,
      7: command7,
      8: command8,
      9: command9,
  }
  # Print command prompt until user inputs x to exit program
  while (True):
      print()
      command = input("Please enter a command (1-9, x to exit): ")
      # Check if input is digit
      if command.strip().isdigit():
          num = int(command)
          if num in commands:
              commands[num](dbConn)
          else:
              # Input was not 1...9
              print("**Error, unknown command, try again...")
      else:
          command = command.strip()
          if command == "x":
              break
          else:
              print("**Error, unknown command, try again...")

#
# command1
#
# Given a connection to the CTA database, prompt user to
# input full or partial name of CTA station and then
# print stations with matching names and their
# corresponding ID
#
def command1(dbConn):
  print()
  name = input("Enter partial station name (wildcards _ and %): ")

  sql = """Select Station_ID, Station_Name From Stations
         Where Station_Name like '{0}'
         group by Station_Name
         order by Station_Name asc;""".format(name)

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql)
  rows = dbCursor.fetchall()

  if len(rows) == 0:
      print("**No stations found...")
  else:
      for row in rows:
          print("{0} : {1}".format(row[0], row[1]))

#
# command2
#
# Given a connection to the CTA database, print stations
# in alphabetical order with corresponding total ridership
#
def command2(dbConn):
  print("** ridership all stations **")

  # First sql prompt is to get total ridership number
  sql1 = """Select Sum(Num_Riders) From Ridership;"""

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql1)
  totalRiders = dbCursor.fetchone()[0]

  # Grab data on total ridership for each station
  sql2 = """Select Stations.Station_Name, 
            SUM(Ridership.Num_Riders)
            From Stations Join Ridership On 
            (Stations.Station_ID = Ridership.Station_ID)
            Group By Stations.Station_Name
            Order By Stations.Station_Name asc"""

  dbCursor.execute(sql2)
  rows = dbCursor.fetchall()

  for row in rows:
      stationName = row[0]
      ridership = row[1]
      # Get corresponding percentage of total ridership
      # for each station
      percentage = getPercentage(ridership, totalRiders)
      print(stationName, ":", f"{ridership:,}",                  
            f"({percentage:.2f}%)")

#
# command3
#
# Given a connection to the CTA database, print 
# Top-10 stations in order of total ridership
#
def command3(dbConn):
  print("** top-10 stations **")

  # Grab total ridership across all stations
  sql1 = """Select Sum(Num_Riders) From Ridership;"""

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql1)
  totalRiders = dbCursor.fetchone()[0]

  # Grab total ridership for each station
  sql2 = """Select Stations.Station_Name, 
          SUM(Ridership.Num_Riders) As riders
          From Stations Join Ridership On 
          (Stations.Station_ID = Ridership.Station_ID)
          Group By Stations.Station_Name
          Order By riders desc
          limit 10"""

  dbCursor.execute(sql2)
  rows = dbCursor.fetchall()

  for row in rows:
      stationName = row[0]
      ridership = row[1]
      # Get corresponding percentage of total ridership
      # for each station
      percentage = getPercentage(ridership, totalRiders)
      print(stationName, ":", f"{ridership:,}",                  
            f"({percentage:.2f}%)")


#
# command4
#
# Given a connection to the CTA database, print 
# Bottom-10 stations in order of total ridership
#
def command4(dbConn):
  print("** least-10 stations **")

  # Grab total ridership across all stations
  sql1 = """Select Sum(Num_Riders) From Ridership;"""

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql1)
  totalRiders = dbCursor.fetchone()[0]

  #Grab total ridership for each station
  sql2 = """Select Stations.Station_Name, 
          SUM(Ridership.Num_Riders) As riders
          From Stations Join Ridership On 
          (Stations.Station_ID = Ridership.Station_ID)
          Group By Stations.Station_Name
          Order By riders asc
          limit 10"""

  dbCursor.execute(sql2)
  rows = dbCursor.fetchall()

  for row in rows:
      stationName = row[0]
      ridership = row[1]
      # Get corresponding percentage of total ridership
      # for each station
      percentage = getPercentage(ridership, totalRiders)
      print(stationName, ":", f"{ridership:,}",                  
            f"({percentage:.2f}%)")


#
# command5
#
# Given a connection to the CTA database, prompt user to
# to enter line color. If it exist print every stop
# (in alphabetical order) on that line with its corresponding
# direction and accessibility status
#
def command5(dbConn):
  print()
  lineColor = input("Enter a line color (e.g. Red or Yellow): ")

  sql = """Select Stops.Stop_Name, Stops.Direction, Stops.ADA
          From Stops Join StopDetails On 
          (Stops.Stop_ID = StopDetails.Stop_ID) join Lines on
          (StopDetails.Line_ID = Lines.Line_ID)
          Where Lines.Color like '{0}'
          Order by Stops.Stop_Name asc""".format(lineColor)

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql)
  rows = dbCursor.fetchall()

  if len(rows) == 0:
      print("**No such line...")
  else:
      for row in rows:
          name = row[0]
          direction = row[1]
          accessible = row[2]
          ADA = "no"
          if accessible == 1:
              ADA = "yes"
          output = "{0} : direction = {1} (accessible? {2})"
          print(output.format(name, direction, ADA))

#
# command6
#
# Given a connection to the CTA database, print total monthly
# ridership across all the stations for each month of the year.
# Then prompt user to graph data using mathplot.lib
#
def command6(dbConn):
  print("** ridership by month **")
  sql = """Select strftime('%m', Ride_Date) As Month,           
           sum(Num_Riders) 
           from Ridership
           group by Month
           order by Month asc;"""

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql)
  rows = dbCursor.fetchall()

  for row in rows:
      month = row[0]
      ridership = row[1]
      print(month, ":", f"{ridership:,}")

  print()
  # Prompt user to graph data
  plot = input("Plot? (y/n)")

  if plot == "y":
      x = []  # create 2 empty vectors/lists
      y = []
      # append each (x, y) coordinate that you want to plot
      for row in rows:
          x.append(row[0])
          y.append(row[1])

      plt.ioff()
      plt.xlabel("month")
      plt.ylabel("number of riders")
      plt.title("monthly ridership")
      plt.plot(x, y)
      plt.show()

#
# command7
#
# Given a connection to the CTA database, print total yearly
# ridership across all the stations for each year in the database.
# Then prompt user to graph data using mathplot.lib
#
def command7(dbConn):
  print("** ridership by year **")
  sql = """Select strftime('%Y', Ride_Date) As Year,       
           sum(Num_Riders) 
           from Ridership
           group by Year
           order by Year asc;"""

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql)
  rows = dbCursor.fetchall()

  for row in rows:
      year = row[0]
      ridership = row[1]
      print(year, ":", f"{ridership:,}")

  print()
  # Prompt user to graph data
  plot = input("Plot? (y/n)")

  if plot == "y":
      x = []  # create 2 empty vectors/lists
      y = []
      # append each (x, y) coordinate that you want to plot
      for row in rows:
          x.append(row[0])
          y.append(row[1])

      plt.xlabel("year")
      plt.ylabel("number of riders")
      plt.title("yearly ridership")
      plt.plot(x, y)
      plt.show()

#
# command8
#
# Given a connection to the CTA database, prompt user to
# input a comparison year, then ask user to input two stations
# to compare. Print ridership for the first 5 and last 5 days
# of the given year for both given stations.
# Then prompt user to graph data using mathplot.lib
#
def command8(dbConn):
  print()
  # Grab year from user
  year = input("Year to compare against? ")
  if not year.isnumeric():
      return

  # Grab first station from user
  print()
  station1Input = input("Enter station 1 (wildcards _ and %): ")

  sql1 = """Select Station_ID, Station_Name From Stations
         Where Station_Name like '{0}';""".format(station1Input)

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql1)
  station1 = dbCursor.fetchall()

  # Check if only one valid station, otherwise return
  if len(station1) == 0:
      print("**No station found...")
      return
  elif len(station1) > 1:
      print("**Multiple stations found...")
      return

  # Grab second station from user
  print()
  station2Input = input("Enter station 2 (wildcards _ and %): ")

  sql2 = """Select Station_ID, Station_Name From Stations
         Where Station_Name like '{0}';""".format(station2Input)

  dbCursor.execute(sql2)
  station2 = dbCursor.fetchall()

  # Check if only one valid station, otherwise return
  if len(station2) == 0:
      print("**No station found...")
      return
  elif len(station2) > 1:
      print("**Multiple stations found...")
      return

  # Grab data from first station with given year
  sql3 = """Select strftime('%Y-%m-%d', Ridership.Ride_Date),   
          Ridership.Num_Riders
          from Ridership join Stations on
          (Ridership.Station_ID = Stations.Station_ID)
          where Stations.Station_Name like '{0}'
          and strftime('%Y', Ridership.Ride_Date) = '{1}'
          group by Ridership.Ride_Date
          order by Ridership.Ride_Date asc;"""
  sql3 = sql3.format(station1Input, year)

  dbCursor.execute(sql3)
  station1Data = dbCursor.fetchall()

  print("Station 1: {0} {1}".format(station1[0][0],     
                                    station1[0][1]))
  # print data for first and last 5 days of year
  for i in range(5):
      print(station1Data[i][0], station1Data[i][1])
  for i in range(len(station1Data) - 5, len(station1Data)):
      print(station1Data[i][0], station1Data[i][1])

  # Grab data from second station with given year
  sql4 = """Select strftime('%Y-%m-%d', Ridership.Ride_Date),   
          Ridership.Num_Riders
          from Ridership join Stations on
          (Ridership.Station_ID = Stations.Station_ID)
          where Stations.Station_Name like '{0}'
          and strftime('%Y', Ridership.Ride_Date) = '{1}'
          group by Ridership.Ride_Date
          order by Ridership.Ride_Date asc;"""
  sql4 = sql4.format(station2Input, year)

  dbCursor.execute(sql4)
  station2Data = dbCursor.fetchall()

  print("Station 2: {0} {1}".format(station2[0][0],     
                                    station2[0][1]))
  # Print data for first and last 5 days of year
  for i in range(5):
      print(station2Data[i][0], station2Data[i][1])
  for i in range(len(station2Data) - 5, len(station2Data)):
      print(station2Data[i][0], station2Data[i][1])

  print()
  # Prompt user to graph data
  plot = input("Plot? (y/n)")

  if plot == "y":
      day = 1
      x = []  # create 3 empty vectors/lists
      y1 = []
      y2 = []
    
      # append each (x, y) coordinate that you want to plot
      for row in station1Data:
          x.append(day)
          y1.append(row[1])
          day += 1

      day = 1
      for row in station2Data:
          y2.append(row[1])
          day += 1

      plt.xlabel("day")
      plt.ylabel("number of riders")
      plt.title("riders of each day of {0}".format(year))
      plt.plot(x, y1)
      plt.plot(x, y2)
      plt.legend([station1[0][1], station2[0][1]])
      plt.show()

#
# command9
#
# Given a connection to the CTA database, prompt user to
# input a line color. If line exist in database, print
# every station (in alphabetical order) on that line with its
# corresponding geocoordinates. Then prompt user to graph
# data on image of chicago
#
def command9(dbConn):
  print()
  # Grab line color from user
  color = input("Enter a line color (e.g. Red or Yellow): ")

  # Get each station on line with its corresponding coordinates
  sql = """Select distinct(Stations.Station_Name),
           Stops.Latitude, Stops.Longitude
           From Stations Join Stops on
           (Stations.Station_ID = Stops.Station_ID) 
           Join StopDetails On 
           (Stops.Stop_ID = StopDetails.Stop_ID) Join Lines on
           (StopDetails.Line_ID = Lines.Line_ID)
           Where Lines.Color like '{0}'
           Order by Stations.Station_Name asc""".format(color)

  dbCursor = dbConn.cursor()
  dbCursor.execute(sql)
  rows = dbCursor.fetchall()

  # If line doesn't exits, return
  if len(rows) == 0:
      print("**No such line...")
      return
  else:
      for row in rows:
          name = row[0]
          lat = row[1]
          long = row[2]
          print("{0} : ({1}, {2})".format(name, lat, long))

  print()
  # Prompt user to graph data on image
  plot = input("Plot? (y/n)")

  if plot == "y":
    # note that longitude are the X values 
    # and latitude are the Y values
    #
    x = []
    y = []
    for row in rows:
      x.append(row[2])
      y.append(row[1])

    image = plt.imread("chicago.png")
    # area covered by the map:
    xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
    plt.imshow(image, extent=xydims)
    plt.title(color + " line")

    #
    # color is the value input by user,
    # we can use that to plot the
    # figure *except* we need to map Purple-Express to Purple:
    #
    if (color.lower() == "purple-express"):
      color = "Purple" # color="#800080"
    
    plt.plot(x, y, "o", c = color)

    #
    # annotate each (x, y) coordinate with its station name:
    #
    for row in rows:
      name = row[0]
      lat = row[1]
      long = row[2]
      plt.annotate(name, (long, lat))
    
    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])
    
    plt.show()

#
# Helper function that returns num's percent of denom
#
def getPercentage(num, denom):
    perc = (num / denom) * 100.0
    return perc


##################################################################
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

print_stats(dbConn)
loopCommandRequest(dbConn)

#
# done
#
