import { useEffect, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { api, getMe } from "../api";
import type { Character, User } from "../api";

export function AdminPage() {
  const [user, setUser] = useState<User | null>(null);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    getMe().then(setUser);
    api.get<Character[]>("/admin/characters").then((response) => setCharacters(response.data));
  }, []);

  async function submit(path: string, payload?: unknown) {
    try {
      await api.post(path, payload);
      setMessage("Изменения применены");
    } catch {
      setMessage("Операция не выполнена");
    }
  }

  function onXp(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    submit(`/admin/characters/${form.get("characterId")}/xp`, { amount: Number(form.get("amount")) });
  }

  function onCurrency(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    submit(`/admin/characters/${form.get("characterId")}/gold`, {
      gold: Number(form.get("gold")),
      silver: Number(form.get("silver")),
      copper: Number(form.get("copper")),
    });
  }

  function onItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    submit(`/admin/characters/${form.get("characterId")}/item`, {
      name: form.get("name"),
      rarity: form.get("rarity"),
      consumable: form.get("consumable") === "on",
    });
  }

  if (user && !user.is_admin) {
    return <p className="panel">Недостаточно прав.</p>;
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <AdminForm title="XP" characters={characters} onSubmit={onXp}>
        <input className="input" name="amount" type="number" placeholder="XP" required />
      </AdminForm>
      <AdminForm title="Валюта" characters={characters} onSubmit={onCurrency}>
        <input className="input" name="gold" type="number" placeholder="gold" defaultValue="0" />
        <input className="input" name="silver" type="number" placeholder="silver" defaultValue="0" />
        <input className="input" name="copper" type="number" placeholder="copper" defaultValue="0" />
      </AdminForm>
      <AdminForm title="Предмет" characters={characters} onSubmit={onItem}>
        <input className="input" name="name" placeholder="название" required />
        <input className="input" name="rarity" placeholder="редкость" defaultValue="common" />
        <label className="flex items-center gap-2 text-sm text-zinc-300">
          <input name="consumable" type="checkbox" /> consumable
        </label>
      </AdminForm>
      <section className="panel lg:col-span-3">
        <h2 className="section-title">Воскрешение</h2>
        <div className="flex flex-wrap gap-2">
          {characters.map((character) => (
            <button
              key={character.id}
              className="button-secondary"
              onClick={() => submit(`/admin/characters/${character.id}/revive`)}
            >
              {character.name}
            </button>
          ))}
        </div>
      </section>
      {message && <p className="panel lg:col-span-3">{message}</p>}
    </div>
  );
}

function AdminForm({
  title,
  characters,
  children,
  onSubmit,
}: {
  title: string;
  characters: Character[];
  children: ReactNode;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="panel space-y-4" onSubmit={onSubmit}>
      <h1 className="section-title">{title}</h1>
      <select className="input" name="characterId" required>
        {characters.map((character) => (
          <option key={character.id} value={character.id}>
            {character.name}
          </option>
        ))}
      </select>
      {children}
      <button className="button">Применить</button>
    </form>
  );
}
