from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_super_admin


class IsStoreManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_store_manager or request.user.is_super_admin)


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_customer


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin or request.user.is_store_manager:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
