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


# REST API
class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer

# Template view for Leaflet map
def library_map(request):
    return render(request, 'libraries/map.html')

def proximity_search(request):
    lng = float(request.GET.get("lng"))
    lat = float(request.GET.get("lat"))
    radius = float(request.GET.get("radius"))  # meters

    user_location = Point(lng, lat, srid=4326)

    qs = (
        Library.objects
        .annotate(distance=Distance("geom", user_location))
        .filter(geom__distance_lte=(user_location, radius))
        .order_by("distance")
    )

    results = [{
        "id": lib.id,
        "name": lib.name,
        "distance": lib.distance.m,
        "coordinates": [lib.geom.x, lib.geom.y],  # ← FIXED
    } for lib in qs]

    return JsonResponse({"results": results})

@csrf_exempt
def polygon_search(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        geojson_data = json.loads(request.body)
        geometry = GEOSGeometry(json.dumps(geojson_data['geometry']))
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    libraries_inside = Library.objects.filter(geom__intersects=geometry)

    # Build GeoJSON FeatureCollection
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

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    return JsonResponse(feature_collection)