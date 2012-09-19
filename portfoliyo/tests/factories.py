"""Model factories."""
import factory

from portfoliyo import model



class UserFactory(factory.Factory):
    FACTORY_FOR = model.User

    username = factory.Sequence(lambda n: "test{0}".format(n))


    @classmethod
    def _prepare(cls, create, **kwargs):
        """Special handling for ``set_password`` method."""
        password = kwargs.pop("password", None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class ProfileFactory(factory.Factory):
    FACTORY_FOR = model.Profile

    user = factory.SubFactory(UserFactory)



class RelationshipFactory(factory.Factory):
    FACTORY_FOR = model.Relationship

    from_profile = factory.SubFactory(ProfileFactory)
    to_profile = factory.SubFactory(ProfileFactory)
    description = ""


class PostFactory(factory.Factory):
    FACTORY_FOR = model.Post

    author = factory.SubFactory(ProfileFactory)
    student = factory.SubFactory(ProfileFactory)
    original_text = 'foo'
    html_text = 'foo'
