"""Model factories."""
import factory

from portfoliyo import model



class SchoolFactory(factory.Factory):
    FACTORY_FOR = model.School

    name = "Some School"
    postcode = factory.Sequence(lambda n: "{0:>05}".format(n))



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
    school = factory.SubFactory(SchoolFactory)



class RelationshipFactory(factory.Factory):
    FACTORY_FOR = model.Relationship

    from_profile = factory.SubFactory(ProfileFactory)
    to_profile = factory.SubFactory(
        ProfileFactory,
        school=factory.ContainerAttribute(
            lambda o, containers: containers[0].from_profile.school),
        )
    description = ""


    @classmethod
    def create(cls, **kwargs):
        """Special handling for school; prevent cross-school relationships."""
        school = kwargs.pop("school", None)
        if school is not None:
            kwargs['from_profile__school'] = school
            kwargs['to_profile__school'] = school
        if ('to_profile__school' in kwargs and
                not 'from_profile__school' in kwargs):
            kwargs['from_profile__school'] = kwargs['to_profile__school']
        if 'to_profile' in kwargs and not 'from_profile' in kwargs:
            kwargs['from_profile__school'] = kwargs['to_profile'].school
        elif 'from_profile' in kwargs and not 'to_profile' in kwargs:
            kwargs['to_profile__school'] = kwargs['from_profile'].school
        rel = super(RelationshipFactory, cls).create(**kwargs)
        if rel.from_profile.school != rel.to_profile.school:
            raise ValueError("Cannot create relationship across schools.")
        return rel


class GroupFactory(factory.Factory):
    FACTORY_FOR = model.Group

    name = "Test Group"
    owner = factory.SubFactory(ProfileFactory)


class PostFactory(factory.Factory):
    FACTORY_FOR = model.Post

    author = factory.SubFactory(ProfileFactory)
    student = factory.SubFactory(ProfileFactory)
    original_text = 'foo'
    html_text = 'foo'


class BulkPostFactory(factory.Factory):
    FACTORY_FOR = model.BulkPost

    author = factory.SubFactory(ProfileFactory)
    group = factory.SubFactory(GroupFactory)
    original_text = 'foo'
    html_text = 'foo'
