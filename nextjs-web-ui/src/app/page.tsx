'use client';
import { FormEvent, useState } from "react";

type Message = {role: string, content: string };

export default function Home() {
  const [messages, setMessages] = useState<Array<Message>>([]);

  async function sendMessage(ev: FormEvent) {
    ev.preventDefault();
    const form = ev.target as HTMLFormElement;
    const fd = new FormData(form);

    const userMessage = { role: 'user', content: fd.get('message') as string };
    setMessages(prev => [...prev,
      userMessage,
      { role: 'assistant', content: '' }
    ]);
    
    form.reset();

    try {
      const response = await fetch('/chat', {
        method: "POST",
        body: JSON.stringify([...messages, userMessage]),
      });
      const reader = response.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        setMessages(prev => prev.with(-1, {
          content: prev.at(-1)!.content + decoder.decode(value),
          role: prev.at(-1)!.role,
        }));
      }
    } catch (error) {
      console.error('Streaming error:', error);
    }
  }

  return (
    <div >
      <main >
        <ul>
          {messages.map(msg => (
            <li>{msg.role}: {msg.content}</li>
          ))}
        </ul>
        <form onSubmit={sendMessage}>
          <input type="text" name="message" />
          <input type="submit" value="Send" />
        </form>
      </main>
    </div>
  );
}
