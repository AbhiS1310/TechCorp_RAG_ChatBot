import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000"
});

export const sendChat = async (query) => {
  const { data } = await api.post("/chat", { query });
  return data;
};

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
};
