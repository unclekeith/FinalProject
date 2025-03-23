
import httpx
from kivy.utils import platform
from libs.applibs.utils import load_cookies, save_cookies  # noqa: F401

online_server_url = "https://embakweaziwe.onrender.com"
offline_server_url = "http://127.0.0.1:8000"

if platform == "android":
    server_url = online_server_url
else:
    server_url = offline_server_url

# Create a Client instance with cookies
def create_client():
    # create a client session (client = create_client()) to use for that session (app lifetime)
    cookies = load_cookies()
    return httpx.Client()


class AuthRoutes:
    def __init__(self, client):
        self.client = client

    def post_register(self, **kwargs):
        '''
        Expected data: application/x-www-form-urlencoded
        Schema: {'$ref': '#/components/schemas/UserCreate'}
        '''
        response =  self.client.post(f'{server_url}/register', follow_redirects=True, **kwargs)

        return response

    def post_login(self, **kwargs):
        '''
        Expected data: application/x-www-form-urlencoded
        Schema: {'$ref': '#/components/schemas/Body_post_login'}
        '''
        response = self.client.post(f'{server_url}/login', follow_redirects=True, **kwargs)
        if response.status_code == 200:  # Assuming 200 is a successful login
            save_cookies(self.client.cookies)

        return response

    def post_logout(self, **kwargs):
        response = self.client.post(f'{server_url}/logout', follow_redirects=True, **kwargs)
        if response.status_code == 200:  # Assuming 200 is a successful logout
            save_cookies({})  # Clear the cookies

        return response


class CoreRoutes:
    def __init__(self, client):
        self.client = client

    def get_all_conversations_endpoint_all_conversations__get(self, **kwargs):
        response =  self.client.get(f'{server_url}/all-conversations/', follow_redirects=True, **kwargs)

        return response

    def get_teacher_chat_history_chat_history__teacher_id__get(self, teacher_id, **kwargs):
        response =  self.client.get(f'{server_url}/chat-history/{teacher_id}', follow_redirects=True, **kwargs)

        return response

    def reply_to_teacher_reply__teacher_id__post(self, teacher_id, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/MessageSchema'}
        '''
        response =  self.client.post(f'{server_url}/reply/{teacher_id}', follow_redirects=True, **kwargs)

        return response

    def get_healthcheck(self, **kwargs):
        response =  self.client.get(f'{server_url}/healthcheck', follow_redirects=True, **kwargs)

        return response

    def post_activate_deactivate_user(self, student_id, **kwargs):
        response =  self.client.post(f'{server_url}/deactivate_or_reactivate/{student_id}', follow_redirects=True, **kwargs)

        return response

    def patch_reset_password(self, email, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/UserPasswordUpdate'}
        '''
        response =  self.client.patch(f'{server_url}/reset-password/{email}', follow_redirects=True, **kwargs)

        return response

    def get_me(self, **kwargs):
        response =  self.client.get(f'{server_url}/me', follow_redirects=True, **kwargs)

        return response


class StudentsRoutes:
    def __init__(self, client):
        self.client = client

    def get_students(self, **kwargs):
        response =  self.client.get(f'{server_url}/student/', follow_redirects=True, **kwargs)

        return response

    def get_student_by_id(self, student_id, **kwargs):
        response =  self.client.get(f'{server_url}/student/{student_id}', follow_redirects=True, **kwargs)

        return response

    def patch_update_student(self, student_id, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/StudentUpdate'}
        '''
        response =  self.client.patch(f'{server_url}/student/update/{student_id}', follow_redirects=True, **kwargs)

        return response

    def delete_student_by_id(self, student_id, **kwargs):
        response =  self.client.delete(f'{server_url}/student/delete/{student_id}', follow_redirects=True, **kwargs)

        return response

    def upload_profile_picture_student_upload__post(self, **kwargs):
        '''
        Expected data: multipart/form-data
        Schema: {'$ref': '#/components/schemas/Body_upload_profile_picture_student_upload__post'}
        '''
        response =  self.client.post(f'{server_url}/student/upload/', follow_redirects=True, **kwargs)

        return response

    def list_user_documents_student_documents__user_id__get(self, user_id, **kwargs):
        response =  self.client.get(f'{server_url}/student/documents/{user_id}', follow_redirects=True, **kwargs)

        return response

    def list_files_student_list__get(self, **kwargs):
        response =  self.client.get(f'{server_url}/student/list/', follow_redirects=True, **kwargs)

        return response

    def download_document_student_documents__user_id__download_get(self, user_id, **kwargs):
        response =  self.client.get(f'{server_url}/student/documents/{user_id}/download', follow_redirects=True, **kwargs)

        return response


class StudentsubjectsRoutes:
    def __init__(self, client):
        self.client = client

    def get_student_subjects(self, **kwargs):
        response =  self.client.get(f'{server_url}/student-subject/get-student-subjects', follow_redirects=True, **kwargs)

        return response

    def post_add_student_subject(self, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/SubjectCreate'}
        '''
        response =  self.client.post(f'{server_url}/student-subject/add-student-subject', follow_redirects=True, **kwargs)

        return response

    def post_bulk_add_student_subject(self, **kwargs):
        '''
        Expected data: application/json
        Schema: {'type': 'array', 'items': {'$ref': '#/components/schemas/SubjectCreate'}, 'title': 'Subjects'}
        '''
        response =  self.client.post(f'{server_url}/student-subject/add-bulk-student-subjects', follow_redirects=True, **kwargs)

        return response

    def delete_student_subject(self, **kwargs):
        response =  self.client.delete(f'{server_url}/student-subject/remove-student-subject', follow_redirects=True, **kwargs)

        return response

    def upload_file_student_subject_upload__post(self, **kwargs):
        '''
        Expected data: multipart/form-data
        Schema: {'$ref': '#/components/schemas/Body_upload_file_student_subject_upload__post'}
        '''
        response =  self.client.post(f'{server_url}/student-subject/upload/', follow_redirects=True, **kwargs)

        return response

    def get_uploaded_certificate_student_subject_certificate__student_id__get(self, student_id, **kwargs):
        response =  self.client.get(f'{server_url}/student-subject/certificate/{student_id}', follow_redirects=True, **kwargs)

        return response


class SubjectsRoutes:
    def __init__(self, client):
        self.client = client

    def get_subjects(self, **kwargs):
        response =  self.client.get(f'{server_url}/subjects/list', follow_redirects=True, **kwargs)

        return response

    def post_add_subject(self, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/SubjectCreate'}
        '''
        response =  self.client.post(f'{server_url}/subjects/add_one', follow_redirects=True, **kwargs)

        return response

    def post_bulk_add_subject(self, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/SubjectsCreate'}
        '''
        response =  self.client.post(f'{server_url}/subjects/add_many', follow_redirects=True, **kwargs)

        return response

    def patch_update_subject_by_id(self, subject_id, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/SubjectUpdate'}
        '''
        response =  self.client.patch(f'{server_url}/subjects/update/{subject_id}', follow_redirects=True, **kwargs)

        return response

    def delete_subject_by_id(self, subject_id, **kwargs):
        response =  self.client.delete(f'{server_url}/subjects/delete/{subject_id}', follow_redirects=True, **kwargs)

        return response


class TeachersRoutes:
    def __init__(self, client):
        self.client = client

    def send_message_teacher_send_message__post(self, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/MessageSchema'}
        '''
        response =  self.client.post(f'{server_url}/teacher/send-message/', follow_redirects=True, **kwargs)

        return response

    def get_teachers_who_sent_messages_teacher_teachers_who_sent_messages__get(self, **kwargs):
        response =  self.client.get(f'{server_url}/teacher/teachers-who-sent-messages/', follow_redirects=True, **kwargs)

        return response

    def chat_history_teacher_chat_history__get(self, **kwargs):
        response =  self.client.get(f'{server_url}/teacher/chat-history/', follow_redirects=True, **kwargs)

        return response

    def get_replies_endpoint_teacher_get_replies__get(self, **kwargs):
        response =  self.client.get(f'{server_url}/teacher/get-replies/', follow_redirects=True, **kwargs)

        return response

    def get_teachers(self, **kwargs):
        response =  self.client.get(f'{server_url}/teacher/', follow_redirects=True, **kwargs)

        return response

    def get_teacher_by_id(self, teacher_id, **kwargs):
        response =  self.client.get(f'{server_url}/teacher/{teacher_id}', follow_redirects=True, **kwargs)

        return response

    def patch_update_teacher(self, teacher_id, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/TeacherUpdate'}
        '''
        response =  self.client.patch(f'{server_url}/teacher/update/{teacher_id}', follow_redirects=True, **kwargs)

        return response

    def delete_teacher_by_id(self, teacher_id, **kwargs):
        response =  self.client.delete(f'{server_url}/teacher/delete/{teacher_id}', follow_redirects=True, **kwargs)

        return response

    def check_in_staff_by_id(self, teacher_id, **kwargs):
        response =  self.client.patch(f'{server_url}/teacher/Check_In/{teacher_id}', follow_redirects=True, **kwargs)

        return response

    def check_out_staff_by_id(self, teacher_id, **kwargs):
        response =  self.client.patch(f'{server_url}/teacher/Check_Out/{teacher_id}', follow_redirects=True, **kwargs)

        return response

    def upload_file_teacher_upload__post(self, **kwargs):
        '''
        Expected data: multipart/form-data
        Schema: {'$ref': '#/components/schemas/Body_upload_file_teacher_upload__post'}
        '''
        response =  self.client.post(f'{server_url}/teacher/upload/', follow_redirects=True, **kwargs)

        return response

    def list_files_teacher_list__get(self, **kwargs):
        response =  self.client.get(f'{server_url}/teacher/list/', follow_redirects=True, **kwargs)

        return response

    def download_file_teacher_download__filename__get(self, filename, **kwargs):
        response =  self.client.get(f'{server_url}/teacher/download/{filename}', follow_redirects=True, **kwargs)

        return response


class MessagesRoutes:
    def __init__(self, client):
        self.client = client

    def post_send_message(self, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/MessageCreate'}
        '''
        response =  self.client.post(f'{server_url}/message/', follow_redirects=True, **kwargs)

        return response

    def get_messages(self, **kwargs):
        response =  self.client.get(f'{server_url}/message/', follow_redirects=True, **kwargs)

        return response

    def get_message_by_id(self, message_id, **kwargs):
        response =  self.client.get(f'{server_url}/message/{message_id}', follow_redirects=True, **kwargs)

        return response

    def patch_update_message_by_id(self, message_id, **kwargs):
        '''
        Expected data: application/x-www-form-urlencoded
        Schema: {'$ref': '#/components/schemas/MessageUpdate'}
        '''
        response =  self.client.patch(f'{server_url}/message/update/{message_id}', follow_redirects=True, **kwargs)

        return response

    def delete_message_by_id(self, message_id, **kwargs):
        response =  self.client.delete(f'{server_url}/message/delete/{message_id}', follow_redirects=True, **kwargs)

        return response


class ApplicationsRoutes:
    def __init__(self, client):
        self.client = client

    def post_apply(self, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/ApplicationCreate'}
        '''
        response =  self.client.post(f'{server_url}/application/', follow_redirects=True, **kwargs)

        return response

    def get_applications(self, **kwargs):
        response =  self.client.get(f'{server_url}/application/', follow_redirects=True, **kwargs)

        return response

    def get_application_by_id(self, application_id, **kwargs):
        response =  self.client.get(f'{server_url}/application/{application_id}', follow_redirects=True, **kwargs)

        return response

    def patch_approve_application(self, application_id, **kwargs):
        response =  self.client.patch(f'{server_url}/application/approve/{application_id}', follow_redirects=True, **kwargs)

        return response

    def patch_reject_application(self, application_id, **kwargs):
        response =  self.client.patch(f'{server_url}/application/reject/{application_id}', follow_redirects=True, **kwargs)

        return response

    def patch_receive_application(self, application_id, **kwargs):
        response =  self.client.patch(f'{server_url}/application/receive/{application_id}', follow_redirects=True, **kwargs)

        return response

    def patch_pending_application(self, application_id, **kwargs):
        response =  self.client.patch(f'{server_url}/application/pending/{application_id}', follow_redirects=True, **kwargs)

        return response

    def delete_application_by_id(self, application_id, **kwargs):
        response =  self.client.delete(f'{server_url}/application/delete/{application_id}', follow_redirects=True, **kwargs)

        return response


class EventsRoutes:
    def __init__(self, client):
        self.client = client

    def post_create_event(self, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/EventCreate'}
        '''
        response =  self.client.post(f'{server_url}/event/create', follow_redirects=True, **kwargs)

        return response

    def get_events(self, **kwargs):
        response =  self.client.get(f'{server_url}/event/events', follow_redirects=True, **kwargs)

        return response

    def get_event_by_id(self, event_id, **kwargs):
        response =  self.client.get(f'{server_url}/event/list/{event_id}', follow_redirects=True, **kwargs)

        return response

    def patch_update_event_by_id(self, event_id, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/EventUpdate'}
        '''
        response =  self.client.patch(f'{server_url}/event/update/{event_id}', follow_redirects=True, **kwargs)

        return response

    def delete_event_by_id(self, event_id, **kwargs):
        response =  self.client.delete(f'{server_url}/event/delete/{event_id}', follow_redirects=True, **kwargs)

        return response


class CallsRoutes:
    def __init__(self, client):
        self.client = client

    def post_initiate_call(self, receiver_id, **kwargs):
        '''
        Expected data: application/json
        Schema: {'$ref': '#/components/schemas/CallRequest'}
        '''
        response =  self.client.post(f'{server_url}/calls/initiate/{receiver_id}', follow_redirects=True, **kwargs)

        return response

    def delete_end_call(self, receiver_id, **kwargs):
        response =  self.client.delete(f'{server_url}/calls/end/{receiver_id}', follow_redirects=True, **kwargs)

        return response


