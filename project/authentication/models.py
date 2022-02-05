"""Model information for custom users."""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """User manager for QuickSched."""

    def create_user(self, email, password=None):
        """Create normal user accounts. Overriding from BaseUserManager."""
        if not email:
            raise ValueError("Users must have an email address.")

        # 'normalize_email' ensures email is lowercase
        user = self.model(
            email=self.normalize_email(email),
            )

        user.set_password(password)

        # save to applications database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """Create superuser accounts. Overriding from BaseUserManager."""
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )

        # ensure permissions
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        # save to application database
        user.save(using=self._db)
        return user


class CustomUserModel(AbstractBaseUser):
    """Custom user model for QuickSched."""

    class Meta:
        """Metadata regarding custom user models."""

        verbose_name = 'User'
        verbose_name_plural = 'Users'

    email = models.EmailField('Email', max_length=200, unique=True)
    first_name = models.CharField('First name', max_length=50)
    last_name = models.CharField('Last name', max_length=50)
    date_joined = models.DateTimeField('Date joined', auto_now_add=True)
    last_login = models.DateTimeField('Last login', auto_now=True)
    init_changed_password = models.BooleanField(default=False)

    # the following four fields must be overridden to subclass AbstractBaseUser
    # 'is_superuser' is the only field that will be used
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # use email as authentication token
    USERNAME_FIELD = 'email'

    # use the custom user manager defined above
    objects = CustomUserManager()

    def __str__(self):
        """Define human readable name."""
        return self.first_name + ' ' + self.last_name

    def has_perm(self, perm, obj=None):
        """Must be overridden to subclass AbstractBaseUser."""
        return self.is_admin

    def has_module_perms(self, app_label):
        """Must be overridden to subclass AbstractBaseUser."""
        return True
