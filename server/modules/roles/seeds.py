from modules.roles.enums import UserRole
from modules.roles.models import RoleModel

DEFAULT_ROLES = [
    RoleModel(id=UserRole.ADMIN, name="Adminisztrátor"),
    RoleModel(id=UserRole.USER, name="Felhasználó"),
]
