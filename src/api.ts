import axios from "axios";

export type User = {
  id: number;
  username: string;
  email: string;
  karma: number;
  is_admin: boolean;
};

export type Character = {
  id: number;
  name: string;
  class_name: string;
  subclass: string;
  race: string;
  background: string;
  level: number;
  xp: number;
  hp: number;
  armor_class: number;
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  investigation: number;
  route: string;
  is_dead: boolean;
};

export type InventoryItem = {
  id: number;
  name: string;
  rarity: string;
  consumable: boolean;
};

export type Inventory = {
  id: number;
  character_id: number;
  gold: number;
  silver: number;
  copper: number;
  items: InventoryItem[];
};

export const tokenStore = {
  get: () => localStorage.getItem("access_token"),
  set: (token: string) => localStorage.setItem("access_token", token),
  clear: () => localStorage.removeItem("access_token"),
};

export const api = axios.create();

api.interceptors.request.use((config) => {
  const token = tokenStore.get();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      tokenStore.clear();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export async function login(email: string, password: string) {
  const body = new URLSearchParams({ username: email, password });
  const response = await api.post("/login", body);
  tokenStore.set(response.data.access_token);
}

export async function register(username: string, email: string, password: string) {
  await api.post("/users", { username, email, password });
}

export async function getMe() {
  const response = await api.get<User>("/me");
  return response.data;
}

export async function getCharacters() {
  const response = await api.get<Character[]>("/characters");
  return response.data;
}

export async function getInventory(characterId: number) {
  const response = await api.get<Inventory>(`/characters/${characterId}/inventory`);
  return response.data;
}
