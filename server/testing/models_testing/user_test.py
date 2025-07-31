import pytest
from sqlalchemy.exc import IntegrityError
from app import app, db
from models import User, Recipe

@pytest.fixture(scope="module")
def test_client():
    with app.app_context():
        db.create_all()  # Create tables before tests
        yield app.test_client()
        db.session.remove()
        db.drop_all()    # Drop tables after tests

class TestUser:
    def test_has_attributes(self, test_client):
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # create and commit user first to get id
            user = User(username="TestUser", password="testpass")
            db.session.add(user)
            db.session.commit()

            # create recipe linked to that user
            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions=(
                    "Or kind rest bred with am shed then. In raptures building an bringing be. Elderly is detract tedious assured private so to visited. "
                    "Do travelling companions contrasted it. Mistress strongly remember up to. Ham him compass you proceed calling detract. "
                    "Better of always missed we person mr. September smallness northward situation few her certainty something."
                ),
                minutes_to_complete=60,
                user_id=user.id  # assign user id here
            )

            db.session.add(recipe)
            db.session.commit()

            # now verify
            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()
            assert new_recipe is not None
            assert new_recipe.user_id == user.id



    def test_requires_username(self, test_client):
        with app.app_context():
            User.query.delete()
            db.session.commit()

            user = User(password="nopassword")
            db.session.add(user)
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_requires_unique_username(self, test_client):
        with app.app_context():
            User.query.delete()
            db.session.commit()

            user_1 = User(username="Ben", password="pass1")
            user_2 = User(username="Ben", password="pass2")

            db.session.add_all([user_1, user_2])
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_has_list_of_recipes(self, test_client):
        with app.app_context():
            User.query.delete()
            Recipe.query.delete()
            db.session.commit()

            # Create and commit user first to get user.id
            user = User(username="Prabhdip", password="secret")
            db.session.add(user)
            db.session.commit()  # now user.id is assigned

            # Create recipes with user_id explicitly set
            recipe_1 = Recipe(
                title="Delicious Shed Ham",
                instructions=(
                    "Or kind rest bred with am shed then. In raptures building an bringing be. Elderly is detract tedious assured private so to visited. "
                    "Do travelling companions contrasted it. Mistress strongly remember up to. Ham him compass you proceed calling detract. Better of always missed we person mr. September smallness northward situation few her certainty something."
                ),
                minutes_to_complete=60,
                user_id=user.id  # assign user_id explicitly
            )
            recipe_2 = Recipe(
                title="Hasty Party Ham",
                instructions=(
                    "As am hastily invited settled at limited civilly fortune me. Really spring in extent an by. Judge but built gay party world. "
                    "Of so am he remember although required. Bachelor unpacked be advanced at. Confined in declared marianne is vicinity."
                ),
                minutes_to_complete=30,
                user_id=user.id  # assign user_id explicitly
            )

            db.session.add_all([recipe_1, recipe_2])
            db.session.commit()

            assert user.id is not None
            assert recipe_1.id is not None
            assert recipe_2.id is not None

            assert recipe_1 in user.recipes
            assert recipe_2 in user.recipes

