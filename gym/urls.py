from django.urls import path
from gym.views import users_views, people_views, login_view, roles_views, machines_views, exercises_views, routines_views, routineSchedules_views, transactions_views


urlpatterns = [
    path('users/', users_views.user_list, name='users.list'),
    path('users/create/', users_views.create_user, name='users.create'),
    path('users/<int:user_id>/', users_views.user_detail, name='users.getById'),
    path('users/<int:user_id>/update/', users_views.update_user, name='users.update'),
    path('users/<int:user_id>/delete/', users_views.delete_user, name='users.delete'),

    path('people/<str:identification>/', people_views.people_detail_identification, name='people.getByIdentification'),


    path('auth/login', login_view.login, name='login'),

    path('roles/', roles_views.roles_list, name='roles.list'),
    path('roles/create/', roles_views.create_role, name='roles.create'),
    path('roles/<int:role_id>/', roles_views.role_detail, name='roles.getById'),
    path('roles/<int:role_id>/update/', roles_views.update_role, name='roles.update'),
    path('roles/<int:role_id>/delete/', roles_views.delete_role, name='roles.delete'),

    path('machines/', machines_views.machine_list, name='machines.list'),
    path('machines/create/', machines_views.create_machine, name='machines.create'),
    path('machines/<int:machine_id>/', machines_views.machine_detail, name='machines.getById'),
    path('machines/<int:machine_id>/update/', machines_views.update_machine, name='machines.update'),
    path('machines/<int:machine_id>/delete/', machines_views.delete_machine, name='machines.delete'),

    path('exercises/', exercises_views.exercise_list, name='exercises.list'),
    path('exercises/create/', exercises_views.create_exercise, name='exercises.create'),
    path('exercises/<int:exercise_id>/', exercises_views.exercise_detail, name='exercises.getById'),
    path('exercises/<int:exercise_id>/update/', exercises_views.update_exercise, name='exercises.update'),
    path('exercises/<int:exercise_id>/delete/', exercises_views.delete_exercise, name='exercises.delete'),

    path('routines/', routines_views.routine_list, name='routines.list'),
    path('routines/create/', routines_views.create_routine, name='routines.create'),
    path('routines/<int:routine_id>/', routines_views.routine_detail, name='routines.getById'),
    path('routines/<int:routine_id>/update/', routines_views.update_routine, name='routines.update'),
    path('routines/<int:routine_id>/delete/', routines_views.delete_routine, name='routines.delete'),

    path('routineSchedules/', routineSchedules_views.routine_schedules_list, name='routineSchedules.list'),
    path('routineSchedules/<int:people_id>/', routineSchedules_views.routine_schedules_by_people_id, name='routineSchedules.getByPeopleId'),
    path('routineSchedules/create/', routineSchedules_views.create_routine_schedule, name='routineSchedules.create'),
    path('routineSchedules/<int:routine_id>/', routineSchedules_views.routine_schedule_detail, name='routineSchedules.getById'),
    path('routineSchedules/<int:routine_id>/update/', routineSchedules_views.update_routine_schedule, name='routineSchedules.update'),
    path('routineSchedules/<int:routine_id>/delete/', routineSchedules_views.delete_routine_schedule, name='routineSchedules.delete'),
    
    path('transactions/people/<int:people_id>/', transactions_views.getTransactionsByPeopleId, name='transactions.getByPeopleId'),
    path('transactions/create/', transactions_views.create_transaction, name='transactions.create'),
    path('transactions/<int:transaction_id>/', transactions_views.transaction_detail, name='transactions.getById')

]

