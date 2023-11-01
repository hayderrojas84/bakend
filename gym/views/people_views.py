import base64

from django.forms.models import model_to_dict
from django.http import JsonResponse

from gym.models import People
def people_detail_identification(request, identification):
  try:
    people = People.objects.get(identification=identification)
  except People.DoesNotExist:
    return JsonResponse({'message': 'Persona no encontrada'}, status=404)

  if request.method == 'GET':
    data = model_to_dict(people)

    image_data = None
    if people.image:
      image_data = base64.b64encode(people.image).decode('utf-8')

    data['image'] = f"data:image/jpeg;base64,{image_data}" if image_data else None

    return JsonResponse(data)
  return JsonResponse({'message': 'Método no permitido'}, status=405)