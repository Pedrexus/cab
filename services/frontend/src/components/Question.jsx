import React, {useEffect, useState} from 'react';
import {Loading} from "react-simple-chatbot";

const makeURI = question => encodeURI(`http://localhost:8000/ask?question=${question}`)

export default function Question({steps, triggerNextStep}) {
  // this is what the user typed
  const question = steps.question.value;
  const [result, setResult] = useState(null);

  useEffect(() => {
    const uri = makeURI(question);
    fetch(uri).then(response => {
      if (response.ok) {
        response.json().then(obj => {
          setResult(obj.answer);
        })
      }
    });
  }, []);

  // after 1s, the bot goes to the next step automaticlly
  useEffect(() => {
    if (result !== null) {
      const timer = setTimeout(triggerNextStep, 1000);
      return () => clearTimeout(timer);
    }
  }, [result]);

  return (
    <div>
      {result ? result : <Loading />}
    </div>
  )
}