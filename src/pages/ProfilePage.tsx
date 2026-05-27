import { useEffect, useState } from "react";
import { getMe } from "../api";
import type { User } from "../api";

export function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    getMe().then(setUser);
  }, []);

  return (
    <section className="panel max-w-xl">
      <h1 className="section-title">Профиль</h1>
      {user && (
        <div className="space-y-3">
          <p>{user.username}</p>
          <p className="text-zinc-400">{user.email}</p>
          <p>Карма: {user.karma}</p>
          <p>{user.is_admin ? "Мастер" : "Игрок"}</p>
        </div>
      )}
    </section>
  );
}
