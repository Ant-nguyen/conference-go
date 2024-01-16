from django.http import JsonResponse
from .models import Presentation
from common.json import ModelEncoder
from events.api_views import ConferenceListEncoder
from django.views.decorators.http import require_http_methods
import json
from events.models import Conference

class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties =[
        "title",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
    ]
    def get_extra_data(self,o):
        return {"status": o.status.name}


class PresentationEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "conference"
    ]
    encoders={
        "conference":ConferenceListEncoder()
    }
    def get_extra_data(self,o):
        return {"status": o.status.name}


@require_http_methods(["GET",'POST'])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = Presentation.objects.filter(conference=conference_id)
        return JsonResponse(
            {"presentations": presentations},
            encoder=PresentationListEncoder)
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse({"message":"conference is invalid"},status =400)
        presentation = Presentation.create(**content)
        return JsonResponse(presentation,encoder=PresentationListEncoder,safe=False)

@require_http_methods(["GET",'PUT',"DELETE"])
def api_show_presentation(request, id):
    if request.method == "GET":
        presentation =Presentation.objects.get(id=id)
        return JsonResponse(presentation,encoder=PresentationEncoder,safe=False)
    elif request.method == "DELETE":
        count = Presentation.objects.filter(id=id).delete()
        return JsonResponse({"deleted":count[0]>0})
    else:
        content = json.loads(request.body)
        presentation = Presentation.objects.get(id=id)
        try:
            if "conference" in content:
                conference = Conference.objects.filter(id=content["conference"])
                content["conference"] = conference
            if "status" in content:
                if content["status"] != Presentation.objects.get(id=id).status.name:
                    if content["status"] == "APPROVED":
                        presentation.approve()
                    elif content["status"] == "REJECTED":
                        presentation.reject()
                del content["status"]
        except Conference.DoesNotExist:
            return JsonResponse({"message":"conference invalid"},status=400)

        Presentation.objects.filter(id=id).update(**content)

        return JsonResponse(presentation,encoder=PresentationEncoder,safe=False)
