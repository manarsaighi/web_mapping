from django.shortcuts import render
from rest_framework import viewsets
from .models import Library
from .serializers import LibrarySerializer
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.http import JsonResponse
import json
from django.contrib.gis.geos import GEOSGeometry
from .models import Library

from django.views.decorators.csrf import csrf_exempt


# rest api using django rest framework
class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer

# template view for leaflet map
def library_map(request):
    return render(request, 'libraries/map.html')

# proximity search end point
# find libraries within a given radius 
def proximity_search(request):
    # read user coordinates
    lng = float(request.GET.get("lng"))
    lat = float(request.GET.get("lat"))
    radius = float(request.GET.get("radius"))  # meters

    # geofjango point 
    user_location = Point(lng, lat, srid=4326)

    # query distance and filter 
    # compute distance from each library to the point
    # filter the ones within radius and order by nearest first
    qs = (
        Library.objects
        .annotate(distance=Distance("geom", user_location))
        .filter(geom__distance_lte=(user_location, radius))
        .order_by("distance")
    )

    # compile results as json 
    results = [{
        "id": lib.id,
        "name": lib.name,
        "distance": lib.distance.m,
        "coordinates": [lib.geom.x, lib.geom.y],  # ← FIXED
    } for lib in qs]
    # return json response 
    return JsonResponse({"results": results})

# polygon search endpoint
@csrf_exempt
def polygon_search(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        geojson_data = json.loads(request.body)
        geometry = GEOSGeometry(json.dumps(geojson_data['geometry']))
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    # find all libraries whose geometry intersects the polygon 
    libraries_inside = Library.objects.filter(geom__intersects=geometry)

    # create geojson feature collection 
    features = []
    for lib in libraries_inside:
        features.append({
            "type": "Feature",
            "geometry": json.loads(lib.geom.geojson),
            "properties": {
                "id": lib.id,
                "name": lib.name,
                "postcode": lib.postcode,
                "opening_hours": lib.opening_hours
            }
        })
    # wrap into feature collection 
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    # return json response 
    return JsonResponse(feature_collection)