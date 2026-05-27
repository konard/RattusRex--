import { useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../api";

export function LoginPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await login(String(form.get("email")), String(form.get("password")));
      navigate("/characters");
    } catch {
      setError("Не удалось войти");
    }
  }

  return (
    <AuthFrame title="Вход">
      <form className="space-y-4" onSubmit={onSubmit}>
        <input className="input" name="email" type="email" placeholder="email" required />
        <input className="input" name="password" type="password" placeholder="password" required />
        {error && <p className="text-sm text-red-300">{error}</p>}
        <button className="button w-full">Войти</button>
        <Link className="button-secondary block text-center" to="/register">
          Перейти к регистрации
        </Link>
      </form>
    </AuthFrame>
  );
}

export function AuthFrame({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="grid min-h-screen place-items-center bg-ink px-4 text-zinc-100">
      <section className="w-full max-w-md rounded-lg border border-zinc-800 bg-panel p-6 shadow-xl">
        <h1 className="mb-6 text-2xl font-semibold text-ember">{title}</h1>
        {children}
      </section>
    </div>
  );
}
