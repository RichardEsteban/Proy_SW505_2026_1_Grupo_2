import pytest
from app.domain.entities.usuario import Usuario
from app.domain.exceptions.credenciales_invalidas import CredencialesInvalidas
from app.domain.use_cases.accesos.autenticar_usuario import GestionAccesosUseCase
from tests.unit.fakes.fake_repositorio_usuario import FakeRepositorioUsuario

class TestAutenticacionYUsuarios:

    def test_login_credenciales_correctas(self):
        usuario = Usuario(id=1, email="juan@test.com", password_hash="Clave123", rol="vendedor", activo=True)
        fake_repo = FakeRepositorioUsuario([usuario])
        use_case = GestionAccesosUseCase(fake_repo)

        resultado = use_case.autenticar("juan@test.com", "Clave123")
        assert resultado.id == 1

    def test_login_password_incorrecto(self):
        usuario = Usuario(id=1, email="juan@test.com", password_hash="Clave123", rol="vendedor", activo=True)
        fake_repo = FakeRepositorioUsuario([usuario])
        use_case = GestionAccesosUseCase(fake_repo)

        with pytest.raises(CredencialesInvalidas):
            use_case.autenticar("juan@test.com", "clave_erronea")

    def test_login_usuario_inactivo(self):
        usuario = Usuario(id=1, email="juan@test.com", password_hash="Clave123", rol="vendedor", activo=False)
        fake_repo = FakeRepositorioUsuario([usuario])
        use_case = GestionAccesosUseCase(fake_repo)

        with pytest.raises(CredencialesInvalidas):
            use_case.autenticar("juan@test.com", "Clave123")

    def test_cambiar_password_exitoso(self):
        usuario = Usuario(id=1, email="juan@test.com", password_hash="Clave123", rol="vendedor", activo=True)
        fake_repo = FakeRepositorioUsuario([usuario])
        use_case = GestionAccesosUseCase(fake_repo)

        use_case.cambiar_password(usuario_id=1, password_actual="Clave123", nueva_password="NuevaClave99", confirmacion="NuevaClave99")
        assert fake_repo._usuarios[0].password_hash == "NuevaClave99"

    def test_cambiar_password_no_coincide(self):
        usuario = Usuario(id=1, email="juan@test.com", password_hash="Clave123", rol="vendedor", activo=True)
        fake_repo = FakeRepositorioUsuario([usuario])
        use_case = GestionAccesosUseCase(fake_repo)

        with pytest.raises(ValueError, match="La confirmación de la contraseña no coincide"):
            use_case.cambiar_password(usuario_id=1, password_actual="Clave123", nueva_password="NuevaClave99", confirmacion="ClaveDiferente")

    def test_cambiar_password_muy_corta(self):
        usuario = Usuario(id=1, email="juan@test.com", password_hash="Clave123", rol="vendedor", activo=True)
        fake_repo = FakeRepositorioUsuario([usuario])
        use_case = GestionAccesosUseCase(fake_repo)

        with pytest.raises(ValueError, match="La contraseña debe tener al menos 8 caracteres y un número"):
            use_case.cambiar_password(usuario_id=1, password_actual="Clave123", nueva_password="short", confirmacion="short")
