import base64

from drf_yasg import openapi

from rest_framework import serializers
from datetime import timezone, datetime
from gym.models import Users, People, Exercises, Machines, ExerciseMachines, Transactions, Routines, RoutinesExercises, RoutineSchedules, UserRoles, Maintenances
from django.core.exceptions import FieldDoesNotExist

class BaseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance, show_created_updated=False):
        representation = super().to_representation(instance)

        if not show_created_updated:
            for field_name in ['created', 'updated']:
                representation.pop(field_name, None)

        image_field_name = 'image'
        try:
            image_field = instance._meta.get_field(image_field_name)
        except FieldDoesNotExist:
            return representation

        if image_field:
            image_data = getattr(instance, image_field_name, None)
            if image_data is not None:
                image = f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
                representation['image'] = image

        return representation

    class Meta:
        model = None
        fields = '__all__'

class TransactionSerializer(BaseSerializer):
    class Meta:
        model = Transactions
        fields = '__all__'

class PeopleSerializer(BaseSerializer):
    transactions = TransactionSerializer(source='peopleId', read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        transactions = Transactions.objects.filter(peopleId=instance).values()

        representation['paymentStatus'] = 'Pendiente'
    
        if transactions:
            currentDate = datetime.now(timezone.utc).date()
            for transaction in transactions:
                if transaction['endDate'] >= currentDate:
                    representation['paymentStatus'] = 'Pagado'

        return representation
    class Meta:
        model = People
        fields = '__all__'

class UserSerializer(BaseSerializer):
    people = PeopleSerializer(source='userId', read_only=True)

    def get_people(self, instance):
        people = People.objects.filter(userId=instance).first()
        return PeopleSerializer(people, many=False).data if people else {}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['people'] = self.get_people(instance)
        if 'password' in representation:
            del representation['password']
        return representation

    class Meta:
        model = Users
        fields = '__all__'

class MachineSerializer(BaseSerializer):  
    class Meta:
        model = Machines
        fields = '__all__'

class ExerciseSerializer(BaseSerializer):  
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        exercise_machines = ExerciseMachines.objects.filter(exerciseId=instance)
        machines = [exercise_machine.machineId for exercise_machine in exercise_machines]
        representation['machines'] = MachineSerializer(machines, many=True).data
        return representation

    class Meta:
        model = Exercises
        fields = '__all__'

class ExcersiseCreateSerializer(serializers.Serializer):
    exercise = serializers.ModelField(
        model_field=Exercises,
    )
    machines = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )

class RoutineExerciseSerializer:
    class Meta:
        model = RoutinesExercises
        fields = '__all__'

class RoutineSerializer(BaseSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        routine_exercises = RoutinesExercises.objects.filter(routineId=instance)
        exercises = [routine_exercise.exerciseId for routine_exercise in routine_exercises]
        representation['exercises'] = ExerciseSerializer(exercises, many=True).data
        return representation

    class Meta:
        model = Routines
        fields = '__all__'

class RoutineScheduleSerializer(BaseSerializer):
    routine = RoutineSerializer(read_only=True)

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        routine = Routines.objects.filter(pk=instance.routineId.id).first()
        representation['routine'] = RoutineSerializer(routine, many=False).data if routine else {}
        return representation
    class Meta:
        model = RoutineSchedules
        fields = '__all__'

class UserRoleSerializer(BaseSerializer):
    class Meta:
        model = UserRoles
        fields = '__all__'

class UserCreationSerializer(serializers.Serializer):
    user = serializers.ModelField(
        write_only=True,
        model_field=Users
    )
    people = serializers.ModelField(
        model_field=People,
        write_only=True,
    )
    image = serializers.ImageField(
        write_only=True,
        required=False
    )

    class Meta:
        swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "title": "UserCreation",
            "properties": {
                "user": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "username": openapi.Schema(
                            title="Nombre de usuario",
                            type=openapi.TYPE_INTEGER
                        ),
                        "password": openapi.Schema(
                            title="Constaseña",
                            type=openapi.TYPE_STRING
                        ),
                        "is_active": openapi.Schema(
                            title="Activo",
                            type=openapi.TYPE_BOOLEAN,
                            default=True
                        ),
                    },
                    required=["username", "password"],
                ),
                "people": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "userId": openapi.Schema(
                            title="User ID",
                            type=openapi.TYPE_INTEGER
                        ),
                        "identification": openapi.Schema(
                            title="Identification",
                            type=openapi.TYPE_STRING
                        ),
                        "names": openapi.Schema(
                            title="Names",
                            type=openapi.TYPE_STRING
                        ),
                        "lastnames": openapi.Schema(
                            title="Lastnames",
                            type=openapi.TYPE_STRING
                        ),
                        "birthdate": openapi.Schema(
                            title="Birthdate",
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATE
                        ),
                        "email": openapi.Schema(
                            title="Email",
                            type=openapi.TYPE_STRING
                        ),
                        "address": openapi.Schema(
                            title="Address",
                            type=openapi.TYPE_STRING
                        ),
                        "mobile": openapi.Schema(
                            title="Mobile",
                            type=openapi.TYPE_STRING
                        ),
                        "weight": openapi.Schema(
                            title="Weight",
                            type=openapi.TYPE_INTEGER
                        ),
                        "height": openapi.Schema(
                            title="Height",
                            type=openapi.TYPE_INTEGER
                        ),
                        "bloodType": openapi.Schema(
                            title="Blood Type",
                            type=openapi.TYPE_STRING
                        ),
                        "gender": openapi.Schema(
                            title="Gender",
                            type=openapi.TYPE_STRING,
                            enum=People.GENDERS.values
                        )
                    },
                    required=["identification", "names", "lastnames", "weight", "height", "gender"],
                ),
                "image": openapi.Schema(
                    title="Image",
                    type=openapi.TYPE_FILE,
                ),
            },
            "required": ["user", "people"],
        }


class MaintenanceSerializer(BaseSerializer):
    class Meta:
        model = Maintenances
        fields = '__all__'
