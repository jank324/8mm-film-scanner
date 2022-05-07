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

  const offStyle = "bg-blue-500 hover:bg-blue-700"
  const onStyle = "bg-yellow-500 hover:bg-yellow-700"

  useEffect(() => {
    axios.get(props.target).then(response => {
      setEnabled(response.data.enabled)
      setOn(response.data.on)
    })

    const sse = new EventSource(props.target + "-stream")
    sse.addEventListener("enabled", e => setEnabled(e.data == "True"))
    sse.addEventListener("on", e => setOn(e.data == "True"))
    sse.onerror = e => sse.close()  // TODO: Do something more intelligent

    return () => sse.close()
  }, [])

  const toggle = () => axios.post(props.target)

  return (
    <button className={"aspect-square " + (on ? onStyle : offStyle) + " text-white font-bold py-2 px-4 rounded disabled:bg-red-500"} onClick={toggle} disabled={!enabled}>{props.children} - {on.toString()} / {enabled.toString()}</button>
  )
}

export default App;
