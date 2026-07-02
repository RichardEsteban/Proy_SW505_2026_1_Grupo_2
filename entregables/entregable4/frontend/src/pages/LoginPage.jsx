import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import Button from "@/shared/components/Button";
import Input from "@/shared/components/Input";
import Badge from "@/shared/components/Badge";
import { useAuth } from "@/shared/auth/AuthContext";
import { getDefaultPathForRole } from "@/shared/utils/roleViews";

const ACCESS_OVERVIEW = [
  {
    label: "Administrador General",
    role: "ADMIN",
    description:
      "Gestiona usuarios, productos, categorías, proveedores, órdenes de compra, ubicaciones y reportes.",
  },
  {
    label: "Supervisor de Almacén Central",
    role: "SUPERVISOR_ALMACEN",
    description:
      "Controla inventario central, recepciones, solicitudes de reposición, despachos y movimientos.",
  },
  {
    label: "Supervisor de Sucursal",
    role: "SUPERVISOR_SUCURSAL",
    description:
      "Gestiona inventario de su sede, solicitudes, recepciones, alertas de stock y movimientos.",
  },
  {
    label: "Vendedor",
    role: "VENDEDOR",
    description:
      "Consulta inventario disponible de su sucursal y registra ventas.",
  },
];

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated, usuario } = useAuth();
  const [form, setForm] = useState({
    correoElectronico: "",
    contrasena: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showForceLogin, setShowForceLogin] = useState(false);

  if (isAuthenticated) {
    return <Navigate to={getDefaultPathForRole(usuario?.rol)} replace />;
  }

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submitLogin(extra = {}) {
    setError("");
    setLoading(true);

    try {
      const usuarioLogueado = await login({ ...form, ...extra });
      const target =
        location.state?.from?.pathname ||
        getDefaultPathForRole(usuarioLogueado?.rol);
      navigate(target, { replace: true });
    } catch (err) {
      setError(err.message || "No se pudo iniciar sesión");
      setShowForceLogin(Number(err.status) === 409);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setShowForceLogin(false);
    await submitLogin();
  }

  async function handleForceLogin() {
    setShowForceLogin(false);
    await submitLogin({ forzarCierreSesion: true });
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-10 text-white">
      <div className="mx-auto grid min-h-[calc(100vh-5rem)] max-w-7xl items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <section>
          <p className="text-sm font-bold uppercase tracking-[0.35em] text-slate-400">
            Codex Venta
          </p>
          <h1 className="mt-5 text-4xl font-black tracking-tight sm:text-5xl">
            Sistema de inventario y ventas.
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
            ¡Hola de nuevo! Todo listo para gestionar tus inventarios y ventas
            hoy. Inicia sesión para comenzar.
          </p>

          <div className="mt-8 grid gap-3 md:grid-cols-2">
            {ACCESS_OVERVIEW.map((account) => (
              <div
                key={account.role}
                className="rounded-2xl border border-slate-700 bg-slate-900/70 p-4 text-left text-slate-100"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="font-black">{account.label}</p>
                  <Badge tone="slate">{account.role}</Badge>
                </div>
                <p className="mt-2 text-sm opacity-80">{account.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-3xl bg-white p-6 text-slate-950 shadow-2xl sm:p-8">
          <div className="mb-6">
            <h2 className="text-2xl font-black">Iniciar sesión</h2>
            <p className="mt-1 text-sm text-slate-500">
              Ingresa con tu correo registrado y contraseña.
            </p>
          </div>

          {error && (
            <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
              <p>{error}</p>
              {showForceLogin && (
                <button
                  type="button"
                  className="mt-3 rounded-xl bg-red-600 px-4 py-2 text-xs font-bold uppercase tracking-wide text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={handleForceLogin}
                  disabled={loading}
                >
                  Cerrar sesión anterior y entrar
                </button>
              )}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <Input
              label="Correo electrónico"
              type="email"
              name="correoElectronico"
              value={form.correoElectronico}
              onChange={handleChange}
              autoComplete="email"
              placeholder="usuario@correo.com"
              required
            />
            <Input
              label="Contraseña"
              type="password"
              name="contrasena"
              value={form.contrasena}
              onChange={handleChange}
              autoComplete="current-password"
              placeholder="Ingresa tu contraseña"
              required
            />
            <div className="flex items-center justify-between text-sm">
              <Link
                to="/recuperar-contrasena"
                className="font-semibold text-slate-700 underline-offset-4 hover:underline"
              >
                ¿Olvidaste tu contraseña?
              </Link>
            </div>
            <Button className="w-full" type="submit" disabled={loading}>
              {loading ? "Ingresando..." : "Entrar"}
            </Button>
          </form>
        </section>
      </div>
    </main>
  );
}
