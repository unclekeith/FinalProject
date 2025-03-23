# from auth.utils import JWTAuth
from admin.admin import (
    ApplicationAdmin,
    # CallAdmin,
    EventsAdmin,
    FileAdmin,
    MessageAdmin,
    MessagesAdmin,
    SubjectAdmin,
    UserAdmin,
    UserSubjectAssociationAdmin,
    StudentAdmin,
    StudentPictureAdmin,
)
from application.routers import application_router  # noqa: F401
from auth.routers import auth_router  # noqa: F401
from calls.routers import call_router  # noqa: F401
from core.routers import core_router  # noqa: F401
from database.core import async_engine  # noqa: F401
from events.routers import events_router  # noqa: F401
from fastapi_offline import FastAPIOffline
from messages.routers import message_router  # noqa: F401
from sqladmin import Admin
from student.routers import student_router, student_subject_router  # noqa: F401
from subject.routers import subject_router  # noqa: F401
from teacher.routers import teacher_router  # noqa: F401

app = FastAPIOffline()
admin = Admin(app=app, engine=async_engine)
# Add the Authentication middleware
# app.add_middleware(JWTAuth)


app.include_router(auth_router)
app.include_router(core_router)
app.include_router(student_router)
app.include_router(student_subject_router)
app.include_router(subject_router)
app.include_router(teacher_router)
app.include_router(message_router)
app.include_router(application_router)
app.include_router(events_router)

app.include_router(call_router)


# app.include_router(parent_router)
# app.include_router(admin_router)
app.include_router(auth_router)
# app.include_router(authenticated_router)


# Admin Routing
admin.add_view(UserAdmin)
admin.add_view(SubjectAdmin)
admin.add_view(MessageAdmin)
admin.add_view(ApplicationAdmin)
admin.add_view(EventsAdmin)
admin.add_view(UserSubjectAssociationAdmin)
admin.add_view(FileAdmin)
admin.add_view(MessagesAdmin)
admin.add_view(StudentPictureAdmin)
admin.add_view(StudentAdmin)

# .add_view(AdministratorUserAdmin)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
