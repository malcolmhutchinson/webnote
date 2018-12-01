"""webnote.GPXFILE. Classes exploiting spatial data in gpx files.

"""

import gpxpy
import os


class GPXFile():
    """Class to handle a gpx file.

    Provide methods to display the data inside a gpx file. Lists of
    routes, tracks, and waypoints.

    """

    gpx = None    # Parsed gpxpy object.
    warnings = []

    def __init__(self, gpxfile):
        """Parse the file with gpxpy.

        Consumes an element from gpxpy, or an opened file. Returns a
        dictionary of gps data values.

        """

        self.gpxfile = gpxfile
        self.gpx = gpxpy.parse(gpxfile)

    def analyse(self):
        """Return a dictionary containing lists of routes, tracks and
        waypoints .

        """

        (path, name) = os.path.split(self.gpxfile.name)

        result = {
            "name": name,
            "routes": self.analyse_routes(),
            "tracks": self.analyse_tracks(),
            "waypoints": self.analyse_waypoints(),
        }

        return result

    def analyse_routes(self):
        """List basic data about each route."""

        result = []
        return result

    def analyse_tracks(self):
        """List basic data about each track."""

        result = []

        for track in self.gpx.tracks:
            points = 0
            for segment in track.segments:
                points += len(segment.points)

            trackrec = {
                "name": track.name,
                "segments": len(track.segments),
                "points": points,
            }

            result.append(trackrec)

        return result

    def analyse_waypoints(self):
        """List basic data about each waypoint."""

        result = []

        for waypoint in self.gpx.waypoints:
            point = {
                "name": waypoint.name,
                "comment": waypoint.comment,
                "latitude": waypoint.latitude,
                "longitude": waypoint.longitude,
                "elevation": waypoint.elevation,
                "time": waypoint.time,
            }

            result.append(point)

        return result
