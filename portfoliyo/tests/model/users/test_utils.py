"""Tests for user model utilities."""
from portfoliyo import model

from portfoliyo.tests import factories


class TestUserNetworks(object):
    def test_simple(self):
        rel1 = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create()

        assert model.utils.user_networks() == [
            {rel1.from_profile_id, rel1.to_profile_id},
            {rel2.from_profile_id, rel2.to_profile_id},
            ]


    def test_joined_by_elder(self):
        rel1 = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(
            from_profile=rel1.elder)

        assert model.utils.user_networks() == [
            {
                rel1.from_profile_id,
                rel1.to_profile_id,
                rel2.to_profile_id,
                },
            ]


    def test_joined_by_student(self):
        rel1 = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(
            to_profile=rel1.student)

        assert model.utils.user_networks() == [
            {
                rel1.from_profile_id,
                rel1.to_profile_id,
                rel2.from_profile_id,
                },
            ]


    def test_merge_networks(self):
        rel1 = factories.RelationshipFactory.create()
        rel2 = factories.RelationshipFactory.create(school=rel1.elder.school)
        factories.RelationshipFactory.create(
            from_profile=rel1.from_profile, to_profile=rel2.to_profile)

        assert model.utils.user_networks() == [
            {
                rel1.from_profile_id,
                rel1.to_profile_id,
                rel2.from_profile_id,
                rel2.to_profile_id
                },
            ]
