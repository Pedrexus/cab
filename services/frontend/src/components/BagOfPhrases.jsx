import {useEffect, useState} from 'react';

function choose(choices) {
  const index = Math.floor(Math.random() * choices.length);
  return choices[index];
}

export default function RandomPhrase({ options }) {
  const [result, setResult] = useState(null);

  useEffect(() => {
    const choice = choose(options);
    setResult(choice);
  }, []);

  return result;
}