from django.urls import path
from gym.views.rest_framework import rf_exercises_views, rf_login_view, rf_machines_views, rf_people_views, rf_transactions_views, rf_routines_views, rf_routineSchedules_views, rf_users_views, rf_maintenances_views

urlpatterns = [
    path('users/', rf_users_views.UsersListView.as_view(), name='users.list'),
    path('users/paginated/', rf_users_views.UsersListPaginatedView.as_view(), name='users.list.paginated'),
    path('users/<int:pk>/', rf_users_views.UserDetailView.as_view(), name='users.detail'),
    path('users/create/', rf_users_views.UserCreateView.as_view(), name='users.create'),
    path('users/<int:pk>/update/', rf_users_views.UserUpdateView.as_view(), name='users.update'),
    path('users/<int:pk>/delete/', rf_users_views.UserDeleteView.as_view(), name='users.delete'),

    path('people/', rf_people_views.PeopleListView.as_view(), name='people.list'),
    path('people/<str:identification>/', rf_people_views.PeopleDetailByIdentificationView.as_view(), name='people.detailByIdentification'),

    path('auth/login', rf_login_view.LoginView.as_view(), name='login'),

    path('machines/', rf_machines_views.MachinesListView.as_view(), name='machines.list'),
    path('machines/paginated/', rf_machines_views.MachinesListPaginatedView.as_view(), name='machines.list.paginated'),
    path('machines/<int:pk>/', rf_machines_views.MachineDetailView.as_view(), name='machines.detail'),
    path('machines/create/', rf_machines_views.MachineCreateView.as_view(), name='machines.create'),
    path('machines/<int:pk>/update/', rf_machines_views.MachineUpdateView.as_view(), name='machines.update'),
    path('machines/<int:pk>/delete/', rf_machines_views.MachineDeleteView.as_view(), name='machines.delete'),
    
    path('maintenances/', rf_maintenances_views.MaintenancesListView.as_view(), name='maintenances.list'),
    path('maintenances/paginated/', rf_maintenances_views.MaintenancesListPaginatedView.as_view(), name='maintenances.list.paginated'),
    path('maintenances/<int:pk>/', rf_maintenances_views.MaintenanceDetailView.as_view(), name='maintenances.detail'),
    path('maintenances/create/', rf_maintenances_views.MaintenanceCreateView.as_view(), name='maintenances.create'),

    path('exercises/', rf_exercises_views.ExerciseListView.as_view(), name='exercises.list'),
    path('exercises/paginated/', rf_exercises_views.ExerciseListPaginatedView.as_view(), name='exercises.list.paginated'),
    path('exercises/<int:pk>/', rf_exercises_views.ExerciseDetailView.as_view(), name='exercises.detail'),
    path('exercises/create/', rf_exercises_views.ExerciseCreateView.as_view(), name='exercises.create'),
    path('exercises/<int:pk>/update/', rf_exercises_views.ExerciseUpdateView.as_view(), name='exercises.update'),
    path('exercises/<int:pk>/delete/', rf_exercises_views.ExerciseDeleteView.as_view(), name='exercises.delete'),

    path('routines/', rf_routines_views.RoutinesListView.as_view(), name='routines.list'),
    path('routines/paginated/', rf_routines_views.RoutineListPaginatedView.as_view(), name='routines.list.paginated'),
    path('routines/<int:pk>/', rf_routines_views.RoutineDetailView.as_view(), name='routines.detail'),
    path('routines/create/', rf_routines_views.RoutineCreateView.as_view(), name='routines.create'),
    path('routines/<int:pk>/update/', rf_routines_views.RoutineUpdateView.as_view(), name='routines.update'),
    path('routines/<int:pk>/delete/', rf_routines_views.DeleteRoutineView.as_view(), name='routines.delete'),

    path('routineSchedules/', rf_routineSchedules_views.RoutineSchedulesListView.as_view(), name='routineSchedules.list'),
    path('routineSchedules/people/<int:people_id>/', rf_routineSchedules_views.RoutineSchedulesByPeopleIdView.as_view(), name='routineSchedules.list.byPeopleId'),
    path('routineSchedules/<int:pk>/', rf_routineSchedules_views.RoutineScheduleDetailView.as_view(), name='routineSchedules.detail'),
    path('routineSchedules/create/', rf_routineSchedules_views.RoutineScheduleCreateView.as_view(), name='routineSchedules.create'),
    path('routineSchedules/<int:pk>/update/', rf_routineSchedules_views.RoutineScheduleUpdateView.as_view(), name='routineSchedules.update'),
    path('routineSchedules/<int:pk>/delete/', rf_routineSchedules_views.RoutineScheduleDeleteView.as_view(), name='routineSchedules.delete'),

    path('transactions/', rf_transactions_views.TransactionsListView.as_view(), name='transactions.list'),
    path('transactions/paginated/', rf_transactions_views.TransactionsListPaginatedView.as_view(), name='transactions.list.paginated'),
    path('transactions/<int:pk>/', rf_transactions_views.TransactionDetailView.as_view(), name='transactions.detail'),
    path('transactions/people/<int:people_id>/', rf_transactions_views.TransactionsByPeopleId.as_view(), name='transactions.list.byPeopleId'),
    path('transactions/create/', rf_transactions_views.TransactionCreateView.as_view(), name='transactions.create'),
]

