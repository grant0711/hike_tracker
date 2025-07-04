*** How to run:


1) Download data from Forerunner 305 into local files
plug in the Forerunner 305 and then run:

```
docker-compose run app
```

2) Python command to read local files and convert to
xml format and save to file within garmin_data/xml/

```
docker-compose run app python convert_gmn_to_xml.py
```

3) TODO Python command to ingest the newly created .xml files
and store in postgres database

4) Downstream processing steps:

- Once stored in database, API layer will be created
to allow access to point and time data
- Frontend application will access data and process
into charts/graphs suitable for monitoring physical
activity of a specific hike

What will this frontend look like:

- Viewing of "Hikes" sorted by date of hike performed
- View total distance of hike
- View total time of hike
- View overall pace (distance/time)
- Display max heart rate
- Display grade of hike/time
- Display heart rate zone/time
- Display calculated time spent Zone 1, 2, 3, 4
- Display the route overlaid via an embedded map image within
  the page
