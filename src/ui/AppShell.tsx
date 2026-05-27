import { LogOut, Shield, ShoppingBag, UserRound, UsersRound } from "lucide-react";
import { NavLink, Navigate, Outlet, useNavigate } from "react-router-dom";
import { tokenStore } from "../api";

const navItems = [
  { to: "/characters", label: "Персонажи", icon: UsersRound },
  { to: "/shop", label: "Магазин", icon: ShoppingBag },
  { to: "/profile", label: "Профиль", icon: UserRound },
  { to: "/admin", label: "Админ", icon: Shield },
];

export function AppShell() {
  const navigate = useNavigate();

  if (!tokenStore.get()) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-ink text-zinc-100">
      <header className="sticky top-0 z-20 border-b border-zinc-800 bg-ink/95 backdrop-blur">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div className="text-lg font-semibold text-ember">DnD Cabinet</div>
          <div className="flex flex-wrap items-center gap-2">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink key={to} to={to} className="nav-link">
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            ))}
            <button
              className="icon-button"
              title="Выйти"
              onClick={() => {
                tokenStore.clear();
                navigate("/login");
              }}
            >
              <LogOut size={18} />
            </button>
          </div>
        </nav>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
