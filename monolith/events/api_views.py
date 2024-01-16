from django.http import JsonResponse
from common.json import ModelEncoder
from .models import Conference, Location, State
from django.views.decorators.http import require_http_methods
import json
from .acls import get_location_pexelapi,get_weather


class LocationListEncoder(ModelEncoder):
    model = Location
    properties =["name","picture_url"]

class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders ={
        "location": LocationListEncoder()
    }

class ConferenceListEncoder(ModelEncoder):
    model =Conference
    properties = [
        "name",
    ]


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url"
    ]

    def get_extra_data(self,o):
        return {'state':o.state.abbreviation}



@require_http_methods(["GET","POST"])
def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceListEncoder,
        )
    else:
        content =json.loads(request.body)
        try:
            location =Location.objects.get(id =content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse({"message":"Location does not exist yet in Database"},status =400)
        conference = Conference.objects.create(**content)
        return JsonResponse(conference,encoder=ConferenceListEncoder,safe=False)

@require_http_methods(["GET","PUT","DELETE"])
def api_show_conference(request, id):
    if request.method == "GET":
        conference = Conference.objects.get(id=id)
        city = conference.location.city
        return JsonResponse(
            {"weather":get_weather(city),"conferences": conference},
            encoder=ConferenceDetailEncoder,
            safe=False,)

    elif request.method == "DELETE":
        count = Conference.objects.filter(id=id).delete()
        return JsonResponse({"deleted":count[0]>0})
    else:
        content = json.loads(request.body)
        try:
            if "location" in content:
                location = Location.objects.get(id = content["location"])
                content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse({"message":"location is not valid"},status=False)
        Conference.objects.filter(id=id).update(**content)
        conference = Conference.objects.filter(id=id)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False)


@require_http_methods(["GET","POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            locations,
            encoder=LocationListEncoder,
            safe=False)
    else:
        content =json.loads(request.body)
        try:
            state =State.objects.get(abbreviation =content["state"])
        except State.DoesNotExist:
            return JsonResponse({"message":"Invalid state abbreviation"},status=400)
        content["state"]=state
        #add url to content
        content.update(get_location_pexelapi(content["city"]))
        location =Location.objects.create(**content)
        return JsonResponse(location,encoder=LocationDetailEncoder,safe=False)

@require_http_methods(["GET","PUT","DELETE"])
def api_show_location(request, id):
    if request.method == "GET":
        location = Location.objects.get(id=id)
        return JsonResponse(location,encoder=LocationDetailEncoder,safe=False)
    elif request.method == "DELETE":
        count = Location.objects.filter(id=id).delete()
        return JsonResponse({"deleted":count[0]>0})
    else:
        content = json.loads(request.body)
        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"]= state
        except State.DoesNotExist:
            return JsonResponse({"message":"Invalid State abbreviaton"},status=400)
        Location.objects.filter(id=id).update(**content)
        location = Location.objects.get(id=id)
        return JsonResponse(location,encoder=LocationDetailEncoder,safe=False)
