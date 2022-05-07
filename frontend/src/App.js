import React, { useState, useEffect } from "react"
import axios from "axios"

import './App.css';


const flask = route => "http://192.168.178.48:5000" + route


function App() {

  return (
    <div className="flex">
      <Preview />
      <Controls />
    </div>
  )
}


const Preview = () => {
  return (
    <div className="h-screen grow flex justify-center bg-black">
      <img className="h-screen" src={flask("/preview")}></img>
    </div>
  )
}


const Controls = () => {

  return (
    <div className="m-0 flex flex-col w-80">
      <ButtonGrid>
        <Toggle target={flask("/light")}>Light</Toggle>
        <Toggle target={flask("/advance")}>Advance</Toggle>
        <Toggle target={flask("/fastforward")}>Fast-Forward</Toggle>
        <Toggle target={flask("/focuszoom")}>Zoom</Toggle>
      </ButtonGrid>
      <label>Save Frames To</label>
      <input type="text" className="bg-green-200"/>
      <label># Frames</label>
      <input type="text" className="bg-green-200"/>
      <button className="bg-slate-300">Scan</button>
      <p>progress_bar</p>
    </div>
  )
}


const ButtonGrid = (props) => {
  return (
    <div className="grid grid-cols-4 gap-2 m-2">
      {props.children}
    </div>
  )
}


const Toggle = (props) => {

  const [enabled, setEnabled] = useState(true)
  const [on, setOn] = useState(false)

  useEffect(() => {
    axios.get(props.target).then(response => {
      setEnabled(response.data.enabled)
      setOn(response.data.on)
    })

    const sse = new EventSource(props.target + "-stream")
    sse.addEventListener("enabled", e => setEnabled(e.data))
    sse.addEventListener("on", e => setOn(e.data))
    sse.onerror = e => sse.close()  // TODO: Do something more intelligent

    return () => sse.close()
  }, [])

  const toggle = () => axios.post(props.target)

  return (
    <button className="aspect-square bg-slate-300" onClick={toggle} disabled={!enabled}>{props.children} - {on}</button>
  )
}

export default App;
