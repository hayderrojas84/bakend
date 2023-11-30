from rest_framework import generics, status
from rest_framework.response import Response

from gym.models import People
from gym.serializers import PeopleSerializer

class PeopleListView(generics.ListAPIView):
    queryset = People.objects.all()
    serializer_class = PeopleSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PeopleDetailByIdentificationView(generics.RetrieveAPIView):
    queryset = People.objects.all()
    serializer_class = PeopleSerializer
    lookup_field = 'identification'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)