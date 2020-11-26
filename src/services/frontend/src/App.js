import "./App.css";
import ChatBot from "react-simple-chatbot";

const steps = [
  {
    id: '1',
    message: 'What number I am considering?',
    trigger: '2',
  },
  {
    id: '2',
    options: [
      { value: 1, label: 'Number 1', trigger: '4' },
      { value: 2, label: 'Number 2', trigger: '3' },
      { value: 3, label: 'Number 3', trigger: '3' },
    ],
  },
  {
    id: '3',
    message: 'Wrong answer, try again.',
    trigger: '2',
  },
  {
    id: '4',
    message: 'Awesome! You are a telepath!',
    end: true,
  },
];

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <ChatBot steps={steps} />
      </header>
    </div>
  );
}

export default App;
