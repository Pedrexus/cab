import React from 'react';
import "./App.css";
import ChatBot from "react-simple-chatbot";
import Question from "./components/Question.jsx";

const bagOfPhrases = [
  `Ask me another one`,
  `Go on, ask again`,
  `I'm here all day... just for you`,
  `Now ask me a hard one`,
  `Make me another question`,
  `Try me again`,
]

let index = 0
function nextPhrase() {
  const phrase = bagOfPhrases[index % bagOfPhrases.length]
  index++

  return phrase
}

const steps = [
  {
    id: '1',
    message: 'Make me a question',
    trigger: 'question',
  },
  {
    id: 'question',
    user: true,
    trigger: '3',
  },
  {
    id: '3',
    asMessage: true,
    component: <Question />,
    waitAction: true,
    trigger: '4',
  },
  {
    id: '4',
    message: nextPhrase(),
    trigger: 'question',
  },
];

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <ChatBot headerTitle="CAB driver" steps={steps} />
      </header>
    </div>
  );
}

export default App;
