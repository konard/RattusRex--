import { useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../api";
import { AuthFrame } from "./LoginPage";

export function RegisterPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      await register(
        String(form.get("username")),
        String(form.get("email")),
        String(form.get("password")),
      );
      navigate("/login");
    } catch {
      setError("Не удалось создать аккаунт");
    }
  }

  return (
    <AuthFrame title="Регистрация">
      <form className="space-y-4" onSubmit={onSubmit}>
        <input className="input" name="username" placeholder="username" required />
        <input className="input" name="email" type="email" placeholder="email" required />
        <input className="input" name="password" type="password" placeholder="password" required />
        {error && <p className="text-sm text-red-300">{error}</p>}
        <button className="button w-full">Создать аккаунт</button>
        <Link className="button-secondary block text-center" to="/login">
          Войти
        </Link>
      </form>
    </AuthFrame>
  );
}
