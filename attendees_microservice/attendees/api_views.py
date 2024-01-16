from django.http import JsonResponse
from .models import Attendee, ConferenceVO
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json

class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]

class AttendeesListEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "name"
    ]

class AttendeesEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders ={
        "conference": ConferenceVODetailEncoder()
    }

@require_http_methods(["GET","POST"])
def api_list_attendees(request, conference_vo_id=None):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference =conference_vo_id)
        return JsonResponse({"attendees":attendees},encoder=AttendeesListEncoder)
    else:
        content = json.loads(request.body)
        try:
            conference_href = f'/api/conferences/{conference_vo_id}/'
            conference = ConferenceVO.objects.get(import_href=conference_href)
            content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse({"message":"invalid conference id"},status=400)
        attendee = Attendee.objects.create(**content)
        return JsonResponse(attendee,encoder=AttendeesListEncoder,safe=False)

@require_http_methods(["GET","PUT","DELETE"])
def api_show_attendee(request, id):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=id)
        return JsonResponse(attendee,encoder=AttendeesEncoder,safe=False)
    elif request.method =="DELETE":
        count =Attendee.objects.filter(id=id).delete()
        return JsonResponse({"Deleted":count[0]>0})
    else:
        content = json.loads(request.body)
        try:
            if "conference" in content:
                conf=ConferenceVO.objects.get(id=content["conference"])
                content["conference"] = conf
        except ConferenceVO.DoesNotExist:
            return JsonResponse({"Message":"Conference ID not found"},status=400)
        Attendee.objects.filter(id=id).update(**content)
        attendee = Attendee.objects.get(id=id)
        return JsonResponse(attendee,encoder=AttendeesEncoder,safe=False)
