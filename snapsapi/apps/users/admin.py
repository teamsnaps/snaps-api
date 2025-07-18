from django.contrib import admin
from django.db.models import Count, F, Case, When, IntegerField, Q
from django.contrib import messages
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html

from snapsapi.apps.users.models import User, Profile
from snapsapi.apps.core.models import Collection


@admin.action(description="Create default collection for selected users")
def create_default_collection(modeladmin, request, queryset):
    """
    Action to create a default collection for selected users who don't have one.
    """
    created_count = 0
    skipped_count = 0

    for user in queryset:
        # Check if user already has a default collection
        if Collection.objects.filter(owner=user, name='default').exists():
            skipped_count += 1
            continue

        # Create default collection for user
        Collection.objects.create_collection(
            owner=user,
            name='default',
            description=f"Default collection for {user.username}",
            is_public=True
        )
        created_count += 1

    if created_count:
        messages.success(request, f"Successfully created default collection for {created_count} users.")
    if skipped_count:
        messages.info(request, f"Skipped {skipped_count} users who already have a default collection.")


@admin.action(description="Reconcile posts count with actual posts")
def reconcile_posts_count(modeladmin, request, queryset):
    """
    Action to reconcile the posts_count field with the actual count of Post objects.
    This helps maintain data consistency between User.posts_count and the actual number
    of Post objects that reference the User.
    """
    updated_count = 0
    for user in queryset:
        # Get the actual count of posts for this user
        actual_posts_count = user.posts.filter(is_deleted=False).count()

        # Update the user's posts_count if it differs from the actual count
        if user.posts_count != actual_posts_count:
            user.posts_count = actual_posts_count
            user.save(update_fields=['posts_count'])
            updated_count += 1

    if updated_count:
        messages.success(request, f"Successfully updated posts count for {updated_count} users.")
    else:
        messages.info(request, "No users needed their posts count updated.")


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'posts_count', 'actual_posts_count', 'posts_count_diff', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'is_deleted')
    actions = [reconcile_posts_count, create_default_collection]
    change_list_template = 'admin/users/user/change_list.html'

    def get_queryset(self, request):
        """
        Add the actual_posts_count and difference as annotations to the queryset.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            actual_posts_count=Count('posts', filter=Q(posts__is_deleted=False)),
            posts_count_diff=F('actual_posts_count') - F('posts_count')
        )
        return queryset

    def actual_posts_count(self, obj):
        """
        Display the actual count of posts for this user.
        """
        return getattr(obj, 'actual_posts_count', obj.posts.filter(is_deleted=False).count())
    actual_posts_count.short_description = 'Actual Posts Count'
    actual_posts_count.admin_order_field = 'actual_posts_count'

    def posts_count_diff(self, obj):
        """
        Display the difference between actual_posts_count and posts_count.
        Highlight in red if there's a discrepancy.
        """
        diff = getattr(obj, 'posts_count_diff', self.actual_posts_count(obj) - obj.posts_count)
        if diff != 0:
            return format_html('<span style="color: red;">{}</span>', diff)
        return diff
    posts_count_diff.short_description = 'Count Difference'
    posts_count_diff.admin_order_field = 'posts_count_diff'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reconcile-all-posts-count/', self.admin_site.admin_view(self.reconcile_all_posts_count), name='reconcile_all_posts_count'),
            path('create-all-default-collections/', self.admin_site.admin_view(self.create_all_default_collections), name='create_all_default_collections'),
        ]
        return custom_urls + urls

    def reconcile_all_posts_count(self, request):
        """
        View to reconcile posts_count for all users.
        """
        if request.method == 'POST':
            # Get all users
            users = User.objects.all()
            updated_count = 0

            for user in users:
                actual_posts_count = user.posts.filter(is_deleted=False).count()
                if user.posts_count != actual_posts_count:
                    user.posts_count = actual_posts_count
                    user.save(update_fields=['posts_count'])
                    updated_count += 1

            if updated_count:
                messages.success(request, f"Successfully updated posts count for {updated_count} users.")
            else:
                messages.info(request, "No users needed their posts count updated.")

            return redirect('admin:users_user_changelist')

        # If not POST, show confirmation page
        context = {
            'title': 'Reconcile Posts Count for All Users',
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/users/user/reconcile_all_confirm.html', context)

    def create_all_default_collections(self, request):
        """
        View to create default collections for all users who don't have one.
        """
        if request.method == 'POST':
            # Get all users
            users = User.objects.all()
            created_count = 0
            skipped_count = 0

            for user in users:
                # Check if user already has a default collection
                if Collection.objects.filter(owner=user, name='default').exists():
                    skipped_count += 1
                    continue

                # Create default collection for user
                Collection.objects.create_collection(
                    owner=user,
                    name='default',
                    description=f"Default collection for {user.username}",
                    is_public=True
                )
                created_count += 1

            if created_count:
                messages.success(request, f"Successfully created default collection for {created_count} users.")
            if skipped_count:
                messages.info(request, f"Skipped {skipped_count} users who already have a default collection.")

            return redirect('admin:users_user_changelist')

        # If not POST, show confirmation page
        context = {
            'title': 'Create Default Collections for All Users',
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/users/user/create_default_collections_confirm.html', context)


admin.site.register(User, UserAdmin)
