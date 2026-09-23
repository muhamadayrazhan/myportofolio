from django.urls import path

from main.views import (
    show_main,
    show_education,
    create_education,
    edit_education,
    delete_education,
    get_education_json,
    get_education_xml,
    show_experience,
    create_experience,
    edit_experience,
    delete_experience,
    get_experience_json,
    get_experience_xml,
    show_project,
    create_project,
    edit_project,
    delete_project,
    get_project_json,
    get_project_xml,
    toggle_star,
    register,
    login_user,
    logout_user,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    # education
    path("education/", show_education, name="show_education"),
    path("education/add/", create_education, name="create_education"),
    path("education/<uuid:education_id>/edit/", edit_education, name="edit_education"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),
    # experience
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", edit_experience, name="edit_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    # project
    path("project/", show_project, name="show_project"),
    path("project/add/", create_project, name="create_project"),
    path("project/<uuid:project_id>/edit/", edit_project, name="edit_project"),
    path("project/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("project/<uuid:project_id>/star/", toggle_star, name="toggle_star"),
    # authentication
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    # data delivery
    path("api/education/", get_education_json, name="get_education_json"),
    path("api/education/xml/", get_education_xml, name="get_education_xml"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("api/experience/xml/", get_experience_xml, name="get_experience_xml"),
    path("api/project/", get_project_json, name="get_project_json"),
    path("api/project/xml/", get_project_xml, name="get_project_xml"),
]
