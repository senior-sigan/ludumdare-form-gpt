import { useCallback, useEffect, useState } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import './App.css'

function SendMessage({onSend}: {onSend: (msg: string) => void}) {
  const [message, setMessage] = useState("");

  const sendMessage = (event: React.FormEvent<HTMLFormElement>) => {
    console.log('BUM')
    event.preventDefault();
    if (message.trim() === "") {
      // Skip empty messages
      return;
    }
    onSend(message.trim());
    setMessage("");
  }

  return (
    <form className="send-message" onSubmit={(ev) => sendMessage(ev)}>
      <label htmlFor="messageInput" hidden>
        Enter Message
      </label>
      <input
        id="messageInput"
        name="messageInput"
        type="text"
        className="form-input__input"
        placeholder="type message..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button type="submit">Send</button>
    </form>
  );
}


export default function App() {
  const socketUrl = "ws://localhost:8000/ws"
  const [messageHistory, setMessageHistory] = useState<any[]>([]);
  const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl);

  useEffect(() => {
    if (lastMessage !== null) {
      setMessageHistory((prev) => prev.concat(lastMessage.data));
    }
  }, [lastMessage, setMessageHistory]);

  const handleSend = useCallback((msg: string) => sendMessage(JSON.stringify({answer: msg})), []);

  const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  }[readyState];

  return (
    <div>
      <p>The WebSocket is currently {connectionStatus}</p>
      <SendMessage onSend={handleSend}/>
      {messageHistory.map((message, idx) => (
        <p key={idx}>{message}</p>
      ))}
    </div>
  )
}
