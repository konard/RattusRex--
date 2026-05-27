import { Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { api, getCharacters, getInventory } from "../api";
import type { Character, Inventory } from "../api";

export function CharactersPage() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selected, setSelected] = useState<Character | null>(null);
  const [inventory, setInventory] = useState<Inventory | null>(null);

  useEffect(() => {
    getCharacters().then((items) => {
      setCharacters(items);
      setSelected(items[0] ?? null);
    });
  }, []);

  useEffect(() => {
    if (selected) {
      getInventory(selected.id).then(setInventory);
    }
  }, [selected]);

  async function removeItem(itemId: number) {
    if (!selected) return;
    const response = await api.delete<Inventory>(
      `/characters/${selected.id}/inventory/items/${itemId}`,
    );
    setInventory(response.data);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <section>
        <h1 className="section-title">Персонажи</h1>
        <div className="space-y-3">
          {characters.map((character) => (
            <button
              key={character.id}
              className={`character-card ${selected?.id === character.id ? "active" : ""}`}
              onClick={() => setSelected(character)}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold">{character.name}</h2>
                  <p className="text-sm text-zinc-400">
                    {character.class_name} {character.subclass}
                  </p>
                </div>
                <span className="badge">Lv {character.level}</span>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-sm">
                <Stat label="XP" value={character.xp} />
                <Stat label="HP" value={character.hp} />
                <Stat label="KD" value={character.armor_class} />
              </div>
            </button>
          ))}
          {!characters.length && <p className="panel">Персонажи пока не найдены.</p>}
        </div>
      </section>

      <section>
        {selected ? (
          <div className="space-y-6">
            <div className="panel">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-semibold text-ember">{selected.name}</h1>
                  <p className="text-zinc-400">
                    {selected.race || "Раса не указана"} / {selected.background || "Предыстория не указана"}
                  </p>
                </div>
                <span className="badge">{selected.is_dead ? "Мертв" : "Жив"}</span>
              </div>
              <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {[
                  ["Сила", selected.strength],
                  ["Ловкость", selected.dexterity],
                  ["Телосложение", selected.constitution],
                  ["Интеллект", selected.intelligence],
                  ["Мудрость", selected.wisdom],
                  ["Харизма", selected.charisma],
                  ["Расследование", selected.investigation],
                  ["Броня", selected.armor_class],
                ].map(([label, value]) => (
                  <Stat key={label} label={String(label)} value={value} />
                ))}
              </div>
            </div>

            <div className="panel">
              <h2 className="section-title">Инвентарь</h2>
              {inventory && (
                <p className="mb-4 text-sm text-zinc-300">
                  {inventory.gold} золота / {inventory.silver} серебра / {inventory.copper} меди
                </p>
              )}
              <div className="space-y-2">
                {inventory?.items.map((item) => (
                  <div key={item.id} className="item-row">
                    <div>
                      <p className="font-medium">{item.name}</p>
                      <p className="text-sm text-zinc-400">
                        {item.rarity} / {item.consumable ? "расходуемый" : "постоянный"}
                      </p>
                    </div>
                    <button className="icon-button" title="Удалить" onClick={() => removeItem(item.id)}>
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))}
                {inventory && !inventory.items.length && (
                  <p className="text-sm text-zinc-400">Инвентарь пуст.</p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <p className="panel">Выберите персонажа.</p>
        )}
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-md border border-zinc-800 bg-zinc-950/50 p-3">
      <p className="text-xs uppercase text-zinc-500">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}
