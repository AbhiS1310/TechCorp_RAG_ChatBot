import ChatUI from "./components/ChatUI.jsx";
import UploadDocs from "./components/UploadDocs.jsx";
import Header from "./components/Header.jsx";

export default function App() {
  return (
    <div className="min-h-screen bg-stone text-ink">
      <Header />
      <main className="mx-auto grid w-full max-w-6xl gap-6 px-6 pb-12 pt-6 md:grid-cols-[2fr_1fr]">
        <ChatUI />
        <UploadDocs />
      </main>
    </div>
  );
}
