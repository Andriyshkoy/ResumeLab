import { useState } from 'react'
import './App.css'
import appLogo from './assets/resumelab_logo.png'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, justifyContent: 'center' }}>
        <img src={appLogo} alt="ResumeLab logo" style={{ height: 72 }} />
        <h1 style={{ margin: 0 }}>ResumeLab</h1>
      </div>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
    </>
  )
}

export default App
