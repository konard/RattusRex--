import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { api, getCharacters } from "../api";
import type { Character } from "../api";

export function ShopPage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    getCharacters().then(setCharacters);
  }, []);

  async function onBuy(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const characterId = Number(form.get("characterId"));
    const item_price = Number(form.get("item_price"));
    const mercenary_cost = Number(form.get("mercenary_cost"));
    try {
      await api.post(`/characters/${characterId}/shop/buy`, {
        item_name: form.get("item_name"),
        rarity: form.get("rarity"),
        consumable: form.get("consumable") === "on",
        item_price,
        mercenary_cost,
      });
      setMessage(`Покупка успешна. Итоговая стоимость: ${item_price + mercenary_cost}`);
    } catch {
      setMessage("Покупка не удалась");
    }
  }

  async function onSell(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const characterId = Number(form.get("characterId"));
    const item_price = Number(form.get("item_price"));
    const mercenary_cost = Number(form.get("mercenary_cost"));
    try {
      await api.post(`/characters/${characterId}/shop/sell`, {
        item_name: form.get("item_name"),
        item_price,
        mercenary_cost,
      });
      setMessage(`Продажа успешна. Доход: ${item_price - mercenary_cost}`);
    } catch {
      setMessage("Продажа не удалась");
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <ShopForm title="Покупка предмета" characters={characters} onSubmit={onBuy} mode="buy" />
      <ShopForm title="Продажа предмета" characters={characters} onSubmit={onSell} mode="sell" />
      {message && <p className="panel lg:col-span-2">{message}</p>}
    </div>
  );
}

function ShopForm({
  title,
  characters,
  onSubmit,
  mode,
}: {
  title: string;
  characters: Character[];
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  mode: "buy" | "sell";
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
      <input className="input" name="item_name" placeholder="название предмета" required />
      {mode === "buy" && (
        <>
          <input className="input" name="rarity" placeholder="редкость" defaultValue="common" />
          <label className="flex items-center gap-2 text-sm text-zinc-300">
            <input name="consumable" type="checkbox" /> расходуемый
          </label>
          <input className="input" name="search_type" placeholder="тип поиска" />
          <input className="input" name="mercenary_level" type="number" placeholder="уровень наемника" />
        </>
      )}
      <input className="input" name="item_price" type="number" min="0" placeholder="цена" required />
      <input className="input" name="mercenary_cost" type="number" min="0" placeholder="стоимость наемников" defaultValue="0" />
      <button className="button">{mode === "buy" ? "Найти и купить" : "Продать"}</button>
    </form>
  );
}
