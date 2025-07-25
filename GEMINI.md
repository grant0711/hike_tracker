**Project Overview:**
This project is a tool to track hiking fitness goals. It imports data from a Garmin Forerunner 305 device, which is first saved as `.gmn` files and then converted to `.xml` files.

**Key Technologies:**
*   Python 3.13
*   Docker & Docker Compose
*   Pipenv
*   Django
*   PostgreSQL
*   garmin-forerunner-tools

**Current Goal:**
The primary objective is to ingest the data from the `.xml` files into a PostgreSQL database using a Django application.

**Progress So Far:**
1.  A Django project named `hike_tracker` has been created.
2.  A Django app named `importer` has been created within the project.
3.  Django models (`Run`, `Lap`, `TrackPoint`) have been defined in `importer/models.py` based on the structure of an example XML file.
4.  The `Pipfile` has been updated to include `django`, `psycopg2-binary`, and `dj-database-url`.
5.  The Django settings have been configured to use the `importer` app and connect to the database using `dj_database_url`.
6.  The `docker-compose.yml` file has been updated to provide the `DATABASE_URL` to the application container.
7.  The database schema has been successfully migrated to the `hiker_db` PostgreSQL database.
8.  A Django management command has been created to parse the XML files and populate the database.
9.  A `Hike` and its associated `TrackPoint` objects have been successfully imported into the database.

**Challenges Overcome:**
*   Resolved `pipenv` installation and dependency issues within the Docker container by using `docker-compose run` to manage dependencies and then rebuilding the image.
*   Fixed `docker-compose` errors by bringing services down and then back up.
*   Corrected a `NotSupportedError` by upgrading the PostgreSQL version used in the `db` service to be compatible with the Django version.
*   Successfully troubleshooted and resolved database connection errors.

**Next Steps:**
The next step is to find a way to query the `TrackPoint`s for a given hike within the Django admin `Hike` change_view and render the hike in a graph. The x-axis of the graph will be time (in minutes) and the y-axis will be the heart rate at that time. The heart rate data may require smoothing.