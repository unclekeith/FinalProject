from application.models import Application
from core.associations import UserSubjectAssociation
from core.models import User
from events.models import Event
from messages.models import Message
from sqladmin import ModelView
from sqlalchemy.orm import relationship
from subject.models import Subject
from teacher.models import File, Messages
from core.models import  Certificates,ProfilePicture


# Create a model view for UserSubjectAssociation
class UserSubjectAssociationAdmin(ModelView, model=UserSubjectAssociation):
    # Optionally customize the columns displayed in the admin panel
    column_list = [
        UserSubjectAssociation.user_id,
        UserSubjectAssociation.subject_id,
        UserSubjectAssociation.grade,
    ]

    # Add relationships to show in the admin panel
    form_extra_fields = {
        "user": relationship(User, back_populates="subject_associations"),
        "subject": relationship(Subject, back_populates="user_associations"),
    }
    form_columns = ["user", "subject", "grade"]  # Fields for form submission
    column_searchable_list = ["grade", "user"]  # Make grades searchable
    column_filters = ["user", "subject"]  # Add filters for easier searching


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.is_checked_out,
        User.first_name,
        User.last_name,
        User.role,
        User.current_academic_level,
        User.email,
        User.subjects,
        User.is_active,
        User.phone_number,
        User.application,
        User.last_checked_in,
        User.last_checked_out,
        User.teaching_subject,
        User.teacher_id_number,
        User.teacher_gender,
        User.teacher_next_of_kin,
        User.teacher_current_academic_level,
        User.is_deleted,
        User.created_at,
    ]
    column_searchable_list = [
        User.first_name,
        User.phone_number,
    ]


class SubjectAdmin(ModelView, model=Subject):
    column_list = [
        Subject.id,
        Subject.name,
        Subject.students,
        Subject.application,
        Subject.is_deleted,
    ]

    column_labels = {
        "student": "Student",
        "name": "Subject Name",
        "id": "ID",
    }


class MessageAdmin(ModelView, model=Message):
    column_list = [
        Message.id,
        Message.message,
        Message.status,
        Message.created_at,
        Message.is_deleted,
    ]


class ApplicationAdmin(ModelView, model=Application):
    column_list = [
        Application.id,
        Application.applicant,
        Application.applicant_id,
        Application.subjects,
        Application.status,
        Application.is_deleted,
        Application.combination
        
    ]


class EventsAdmin(ModelView, model=Event):
    column_list = [
        Event.id,
        Event.name,
        Event.date,
        Event.is_deleted,
    ]


class FileAdmin(ModelView, model=File):
    column_list = [
        File.id,
        File.filename,
        File.filepath,
        File.uploaded_at,
        File.is_deleted,
    ]


class MessagesAdmin(ModelView, model=Messages):
    column_list = [
        Messages.id,
        Messages.teacher_id,
        Messages.conversation_id,
        Messages.sender,
        Messages.content,
    ]

class StudentAdmin(ModelView, model=Certificates):
    column_list = [
        Certificates.id,
        Certificates.filename,
        Certificates.filepath,
        Certificates.uploaded_at,

    ]

class StudentPictureAdmin(ModelView, model=ProfilePicture):
    column_list = [
        ProfilePicture.id,
        ProfilePicture.filename,
        ProfilePicture.filepath,
        ProfilePicture.uploaded_at,

    ]