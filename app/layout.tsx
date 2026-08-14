import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "AI Academy — практическое обучение искусственному интеллекту",
    template: "%s | AI Academy",
  },
  description:
    "Практическое обучение AI для взрослых, детей и команд: индивидуальные программы, реальные проекты и ответственное использование инструментов.",
  metadataBase: new URL("https://example.com"),
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
