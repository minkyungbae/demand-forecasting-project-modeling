import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/hello")
      .then((res) => res.json())
      .then((data) => {
        setMessage(data.message);
      });
  }, []);

  return (
    <div style={{ padding: "40px" }}>
      <h1>Demand Forcasting 'Blinkit' Top 10 Category</h1>

      <p style={{ whiteSpace: "pre-line" }}>{message}</p>
    </div>
  );
}

export default App;